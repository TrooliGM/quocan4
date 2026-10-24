-- Structural upgrade only. Does NOT reconcile or repair missing conversations.
-- Approved target only; quiesce writes first. No automatic runtime migration.
-- Uses current_schema(): operator must verify it is public on the intended DB.
-- Test harness may use a dedicated synthetic schema, never a Production clone.
BEGIN;
SET LOCAL lock_timeout = '3s';
SET LOCAL statement_timeout = '30s';
DO $migration$
DECLARE
    ns TEXT := current_schema();
    ledger REGCLASS;
    item RECORD;
    col RECORD;
    changed SMALLINT[] := ARRAY[]::SMALLINT[];
    changes TEXT[] := ARRAY[]::TEXT[];
    defaults JSONB := '{}'::JSONB;
    constraints_before JSONB;
    constraints_after JSONB;
    rows_before BIGINT;
    rows_after BIGINT;
    hash_before TEXT;
    hash_after TEXT;
    quota_before TEXT;
    quota_after TEXT;
    missing_before BIGINT;
    missing_after BIGINT;
    missing_sql TEXT;
BEGIN
    IF ns IS NULL OR ns LIKE 'pg_%' THEN
        RAISE EXCEPTION 'STOP: target schema is not an application schema';
    END IF;
    ledger := to_regclass(format('%I.guest_ai_requests', ns));
    IF ledger IS NULL OR NOT EXISTS (SELECT 1 FROM pg_class WHERE oid=ledger AND relkind='r')
       OR EXISTS (SELECT 1 FROM pg_inherits WHERE inhrelid=ledger OR inhparent=ledger) THEN
        RAISE EXCEPTION 'STOP: expected ordinary, non-inherited request ledger';
    END IF;
    -- Same lock order as quota/save: usage -> request -> session.
    EXECUTE format('LOCK TABLE %I.guest_ai_usage IN SHARE MODE',ns);
    EXECUTE format('LOCK TABLE %s IN ACCESS EXCLUSIVE MODE',ledger);
    EXECUTE format('LOCK TABLE %I.advisor_sessions,%I.advisor_temporary_sessions,%I.advisor_guest_claims IN SHARE MODE',ns,ns,ns);
    FOR item IN SELECT unnest(ARRAY['request_id','session_id']) AS name LOOP
        SELECT a.attnum,format_type(a.atttypid,a.atttypmod) AS kind,
               a.attgenerated,a.attidentity,pg_get_expr(d.adbin,d.adrelid) AS expression
          INTO col FROM pg_attribute a LEFT JOIN pg_attrdef d
            ON d.adrelid=a.attrelid AND d.adnum=a.attnum
         WHERE a.attrelid=ledger AND a.attname=item.name AND a.attnum>0 AND NOT a.attisdropped;
        IF NOT FOUND OR col.kind NOT IN ('uuid','text') OR col.attgenerated<>'' OR col.attidentity<>'' THEN
            RAISE EXCEPTION 'STOP: unsupported request identifier column %',item.name;
        END IF;
        IF col.kind='uuid' THEN
            changed := array_append(changed,col.attnum);
            changes := array_append(changes,format('ALTER COLUMN %I TYPE TEXT USING %I::text',item.name,item.name));
            IF col.expression IS NOT NULL THEN
                defaults := defaults || jsonb_build_object(item.name,col.expression);
            END IF;
        END IF;
    END LOOP;
    IF cardinality(changed)>0 THEN
        IF EXISTS (SELECT 1 FROM pg_constraint WHERE contype='f' AND
                    ((conrelid=ledger AND conkey && changed) OR (confrelid=ledger AND confkey && changed))) THEN
            RAISE EXCEPTION 'STOP: identifier foreign key requires a separately reviewed coordinated migration';
        END IF;
        IF EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid=ledger AND contype IN ('c','x') AND conkey && changed)
           OR EXISTS (SELECT 1 FROM pg_trigger WHERE tgrelid=ledger AND NOT tgisinternal)
           OR EXISTS (SELECT 1 FROM pg_index WHERE indrelid=ledger AND (indexprs IS NOT NULL OR indpred IS NOT NULL))
           OR EXISTS (SELECT 1 FROM pg_depend WHERE refclassid='pg_class'::regclass AND refobjid=ledger
                      AND refobjsubid=ANY(changed) AND classid='pg_rewrite'::regclass) THEN
            RAISE EXCEPTION 'STOP: custom CHECK/exclusion/trigger/expression index/view needs review';
        END IF;
    END IF;
    SELECT COALESCE(jsonb_agg(jsonb_build_array(conname,contype,pg_get_constraintdef(oid)) ORDER BY conname),'[]'::jsonb)
      INTO constraints_before FROM pg_constraint WHERE conrelid=ledger;
    EXECUTE format('SELECT count(*),md5(COALESCE(string_agg(to_jsonb(t)::text,E''\n'' ORDER BY request_id::text),'''')) FROM %s t',ledger)
        INTO rows_before,hash_before;
    EXECUTE format('SELECT md5(COALESCE(string_agg(to_jsonb(t)::text,E''\n'' ORDER BY uid),'''')) FROM %I.guest_ai_usage t',ns) INTO quota_before;
    missing_sql := format('SELECT count(*) FROM %s q WHERE NOT EXISTS (SELECT 1 FROM %I.advisor_sessions s WHERE s.id=q.session_id::text AND
        (s.owner=q.uid OR EXISTS (SELECT 1 FROM %I.advisor_guest_claims c WHERE c.guest_uid=q.uid AND c.account_uid=s.owner)))
        AND NOT EXISTS (SELECT 1 FROM %I.advisor_temporary_sessions s WHERE s.id=q.session_id::text AND
        (s.owner=q.uid OR EXISTS (SELECT 1 FROM %I.advisor_guest_claims c WHERE c.guest_uid=q.uid AND c.account_uid=s.owner)))',ledger,ns,ns,ns,ns);
    EXECUTE missing_sql INTO missing_before;
    FOR item IN SELECT key,value FROM jsonb_each_text(defaults) LOOP
        EXECUTE format('ALTER TABLE %s ALTER COLUMN %I DROP DEFAULT',ledger,item.key);
    END LOOP;
    IF cardinality(changes)>0 THEN
        EXECUTE format('ALTER TABLE %s %s',ledger,array_to_string(changes,', '));
    END IF;
    FOR item IN SELECT key,value FROM jsonb_each_text(defaults) LOOP
        EXECUTE format('ALTER TABLE %s ALTER COLUMN %I SET DEFAULT (%s)::text',ledger,item.key,item.value);
    END LOOP;
    IF (SELECT count(*) FROM pg_attribute WHERE attrelid=ledger AND attname IN ('request_id','session_id')
        AND NOT attisdropped AND atttypid='text'::regtype)<>2 THEN
        RAISE EXCEPTION 'STOP: identifier type postflight failed';
    END IF;
    SELECT COALESCE(jsonb_agg(jsonb_build_array(conname,contype,pg_get_constraintdef(oid)) ORDER BY conname),'[]'::jsonb)
      INTO constraints_after FROM pg_constraint WHERE conrelid=ledger;
    EXECUTE format('SELECT count(*),md5(COALESCE(string_agg(to_jsonb(t)::text,E''\n'' ORDER BY request_id::text),'''')) FROM %s t',ledger)
        INTO rows_after,hash_after;
    EXECUTE format('SELECT md5(COALESCE(string_agg(to_jsonb(t)::text,E''\n'' ORDER BY uid),'''')) FROM %I.guest_ai_usage t',ns) INTO quota_after;
    EXECUTE missing_sql INTO missing_after;
    IF rows_before<>rows_after OR hash_before IS DISTINCT FROM hash_after OR quota_before IS DISTINCT FROM quota_after
       OR constraints_before IS DISTINCT FROM constraints_after OR missing_before<>missing_after THEN
        RAISE EXCEPTION 'STOP: row/quota/constraint/session-integrity preservation failed';
    END IF;
    RAISE NOTICE 'Structural conversion preserved % rows; % existing requests have no session. Cause NOT verified; no records repaired.',rows_after,missing_after;
END
$migration$;
COMMIT;
