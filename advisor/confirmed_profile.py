"""Chỉ lưu từng mục đã xác nhận. Không đọc profile LLM cũ làm đồng ý của học sinh."""
import json
import os
from uuid import uuid4
from fastapi import HTTPException
from .store import empty_profile

def postgres_connection():
    from .postgres_store import postgres_connection as connect
    return connect()

def enabled():return os.getenv('ADVISOR_PROFILE_ENABLED','false').lower()=='true'
def require_enabled():
    if not enabled():raise HTTPException(503,'Hồ sơ có xác nhận chưa được bật. Cần migration 006 và cấu hình môi trường thử được duyệt.')

def purge_expired(limit=500):
    """Cho job bảo trì được phê duyệt; không có public endpoint/tự chạy startup.

    Xóa từng lô nội dung khách hết TTL, không trả dữ liệu riêng tư hoặc chạm quota.
    """
    require_enabled()
    if not 1<=limit<=500:raise ValueError('invalid_cleanup_limit')
    with postgres_connection() as db:
        rows=db.execute('''DELETE FROM advisor_profile_items WHERE id IN
            (SELECT id FROM advisor_profile_items WHERE expires_at<=NOW() ORDER BY expires_at
             LIMIT %s FOR UPDATE SKIP LOCKED) RETURNING id''',(limit,)).fetchall()
    return len(rows)

def owner_lock(db,uid):
    db.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',('profile-owner:'+uid,))
    if db.execute('SELECT 1 FROM advisor_guest_claims WHERE guest_uid=%s',(uid,)).fetchone():raise HTTPException(409,'Phiên khách đã được chuyển. Hãy đăng nhập lại.')

def public(row):
    row=dict(row)
    for key in ('id','created_at','updated_at','expires_at'):
        if row.get(key) is not None:row[key]=str(row[key])
    return row

def read(uid):
    if not enabled():return {'enabled':False,'profile':empty_profile(),'items':[]}
    with postgres_connection() as db:
        # Dọn nội dung hết TTL của đúng chủ phiên khi họ quay lại; không động tài khoản khác.
        db.execute('DELETE FROM advisor_profile_items WHERE owner=%s AND expires_at<=NOW()',(uid,))
        rows=db.execute('''SELECT id,category,value,confirmed_by,source_session_id,source_proposal_id,
            metadata,version,created_at,updated_at,expires_at FROM advisor_profile_items
            WHERE owner=%s AND (expires_at IS NULL OR expires_at>NOW()) ORDER BY updated_at DESC LIMIT 80''',(uid,)).fetchall()
    items=[public(r) for r in rows];profile=empty_profile()
    for item in items:
        if item['category'] in profile:profile[item['category']].append(item['value'])
    return {'enabled':True,'profile':profile,'items':items}

def context_items(uid):
    """SELECT tối thiểu cho lượt chat; không cache, không dọn/xóa trong đường đọc AI."""
    if not enabled():return []
    with postgres_connection() as db:
        rows=db.execute("""SELECT category,value,metadata->>'area' AS area FROM advisor_profile_items
            WHERE owner=%s AND metadata->>'status'='confirmed'
              AND (expires_at IS NULL OR expires_at>NOW())
            ORDER BY updated_at DESC LIMIT 80""",(uid,)).fetchall()
    return [dict(row) for row in rows]


def confirm(uid,provider,session,proposal_id,value):
    require_enabled()
    from .analysis_jobs import analysis_for_session
    analysis=analysis_for_session(session)
    analyses=[analysis] if analysis else []
    proposal=next((p for a in reversed(analyses) for p in a['proposed_profile_items'] if p['id']==proposal_id),None)
    if not proposal or proposal['proposed_action']!='confirm':raise HTTPException(422,'Nhận định chưa đủ căn cứ để lưu; hãy làm rõ trước.')
    metadata={'analysis_version':analyses[-1].get('analysis_version',1),'survey_id':analyses[-1]['survey_id'],'evidence':proposal['evidence'],'area':proposal.get('area'),
              'confidence':proposal['confidence'],'inference_type':proposal['inference_type'],
              'original_proposal':proposal['value'],'edited_by_user':value!=proposal['value'],'status':'confirmed'}
    with postgres_connection() as db:
        # Claim/recovery locks usage before session/profile. Match that order.
        from .guest_quota import lock_usage,ensure_unclaimed
        lock_usage(db,uid);ensure_unclaimed(db,uid)
        owner_lock(db,uid)
        db.execute('DELETE FROM advisor_profile_items WHERE owner=%s AND expires_at<=NOW()',(uid,))
        # Xác minh phiên vẫn thuộc UID sau khi khóa; không tin object client.
        owned=None
        for table in ('advisor_sessions','advisor_temporary_sessions'):
            expiry=' AND expires_at>NOW()' if table.endswith('temporary_sessions') else ''
            owned=db.execute(f'SELECT messages FROM {table} WHERE id=%s AND owner=%s{expiry} FOR UPDATE',(session['id'],uid)).fetchone()
            if owned:break
        if not owned:raise HTTPException(404,'Không tìm thấy phiên của bạn.')
        current={'id':session['id'],'messages':json.loads(owned['messages'])}
        latest=analysis_for_session(current)
        latest_proposal=next((p for p in (latest or {}).get('proposed_profile_items',[]) if p['id']==proposal_id),None)
        valid=latest_proposal and latest_proposal['proposed_action']=='confirm'
        if not valid or proposal_id in current['messages'][0].get('profile_rejections',[]):raise HTTPException(409,'Đề xuất đã thay đổi hoặc được bỏ qua; hãy mở lại hồ sơ.')
        existing=db.execute('SELECT id FROM advisor_profile_items WHERE owner=%s AND source_session_id=%s AND source_proposal_id=%s',(uid,session['id'],proposal_id)).fetchone()
        from .profile_proposals import norm
        values=db.execute('SELECT category,value,source_proposal_id FROM advisor_profile_items WHERE owner=%s AND (expires_at IS NULL OR expires_at>NOW())',(uid,)).fetchall()
        if any(row['source_proposal_id'] in latest_proposal.get('replaces',[]) for row in values):raise HTTPException(409,'Mục cũ đã xác nhận. Hãy dùng Chỉnh sửa hoặc Xóa mục đó để xác nhận thay đổi, không tạo mục mâu thuẫn.')
        duplicate=any(row['category']==proposal['category'] and norm(row['value'])==norm(value) for row in values)
        if not existing and not duplicate and len(values)>=80:raise HTTPException(409,'Hồ sơ đã có 80 mục; hãy xem lại trước khi thêm.')
        if not duplicate:db.execute('''INSERT INTO advisor_profile_items(id,owner,category,value,confirmed_by,source_session_id,source_proposal_id,metadata,expires_at)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s::jsonb,CASE WHEN %s THEN NOW()+INTERVAL '2 hours' ELSE NULL END)
            ON CONFLICT(owner,source_session_id,source_proposal_id) DO NOTHING''',(str(uuid4()),uid,proposal['category'],value,uid,session['id'],proposal_id,json.dumps(metadata,ensure_ascii=False),provider=='anonymous'))
    return read(uid)

def edit(uid,provider,item_id,value,version,retain=False):
    require_enabled()
    if retain and provider=='anonymous':raise HTTPException(403,'Khách chỉ lưu tạm; đăng nhập trước khi giữ lâu dài.')
    with postgres_connection() as db:
        owner_lock(db,uid)
        row=db.execute('''UPDATE advisor_profile_items SET value=%s,version=version+1,updated_at=NOW(),
            confirmed_by=%s,metadata=metadata||' {"edited_by_user":true}'::jsonb,
            expires_at=CASE WHEN %s THEN NULL ELSE expires_at END
            WHERE id=%s AND owner=%s AND version=%s AND (expires_at IS NULL OR expires_at>NOW()) RETURNING id''',(value,uid,retain,item_id,uid,version)).fetchone()
        if not row:raise HTTPException(409,'Mục đã thay đổi hoặc không thuộc bạn. Hãy mở lại hồ sơ.')
    return read(uid)

def remove(uid,item_id):
    require_enabled()
    with postgres_connection() as db:
        owner_lock(db,uid)
        db.execute('DELETE FROM advisor_profile_items WHERE id=%s AND owner=%s',(item_id,uid))

def transfer(db,guest,account):
    from .rollout import uid_allowed
    if not uid_allowed(account):return
    if not enabled():return
    # Cùng transaction với claim lịch sử. Giữ TTL, không tự đổi đồng ý tạm thành lâu dài.
    for uid in sorted([guest,account]):
        db.execute('SELECT pg_advisory_xact_lock(hashtextextended(%s,0))',('profile-owner:'+uid,))
    db.execute('UPDATE advisor_profile_items SET owner=%s WHERE owner=%s',(account,guest))

def update_session_metadata(store,uid,session_id,change):
    """Chỉ cập nhật metadata, không ghi đè messages đồng thời."""
    from .postgres_adapter import PostgresConversationStore
    if isinstance(store,PostgresConversationStore):
        with postgres_connection() as db:
            for table in ('advisor_sessions','advisor_temporary_sessions'):
                expiry=' AND expires_at>NOW()' if table.endswith('temporary_sessions') else ''
                row=db.execute(f'SELECT messages FROM {table} WHERE id=%s AND owner=%s{expiry} FOR UPDATE',(session_id,uid)).fetchone()
                if row:
                    messages=json.loads(row['messages']);change(messages)
                    db.execute(f'UPDATE {table} SET messages=%s WHERE id=%s AND owner=%s',(json.dumps(messages,ensure_ascii=False),session_id,uid));break
            else:raise HTTPException(404,'Không tìm thấy cuộc trò chuyện của bạn.')
        return store.get(uid,session_id)
    with store.lock:
        row=store.get(uid,session_id);change(row['messages']);return store.write(uid,row)

def use_profile(store,uid,session_id,use):
    return update_session_metadata(store,uid,session_id,lambda messages:messages[0].update(use_confirmed_profile=use))

def reject_proposal(store,uid,session_id,proposal_id):
    def reject(messages):
        from .analysis_jobs import analysis_for_session
        analysis=analysis_for_session({'messages':messages})
        found=analysis and any(p['id']==proposal_id for p in analysis['proposed_profile_items'])
        if not found:raise HTTPException(404,'Không tìm thấy đề xuất trong cuộc trò chuyện của bạn.')
        rejected=messages[0].setdefault('profile_rejections',[])
        if proposal_id not in rejected:
            if len(rejected)>=80:raise HTTPException(409,'Danh sách đề xuất đã dài. Hãy bắt đầu một cuộc trò chuyện mới.')
            rejected.append(proposal_id)
    return update_session_metadata(store,uid,session_id,reject)
