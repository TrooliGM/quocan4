"""Chỉ đọc metadata schema; không tự sửa hoặc tạo bảng trong runtime."""
TEXT = 'text'
TIME = 'timestamp with time zone'
SESSION = {name: TEXT for name in ('id', 'owner', 'title', 'created_at', 'updated_at', 'messages', 'profile', 'summary')}
EXPECTED = {
    'advisor_sessions': SESSION,
    'advisor_temporary_sessions': {**SESSION, 'expires_at': TIME},
    'guest_ai_usage': {'uid': TEXT, 'used_questions': 'integer', 'updated_at': TIME},
    'guest_ai_requests': {'request_id': TEXT, 'uid': TEXT, 'session_id': TEXT, 'status': TEXT,
                          'updated_at': TIME, 'message_hash': TEXT, 'reservation_token': TEXT, 'lease_until': TIME, 'charge_quota': 'boolean'},
    'advisor_guest_claims': {'guest_uid': TEXT, 'account_uid': TEXT, 'claimed_at': TIME},
    'advisor_chat_rate_limits': {'uid': TEXT, 'window_start': TIME, 'requests': 'integer'},
    'advisor_guest_sessions': {'token_hash': TEXT, 'uid': TEXT, 'created_at': TIME, 'expires_at': TIME},
}


def inspect_schema(db):
    missing_tables, missing_columns, incompatible = [], [], []
    for table, expected in EXPECTED.items():
        rows = db.execute('''SELECT attname, format_type(atttypid,atttypmod) AS data_type
            FROM pg_attribute WHERE attrelid=to_regclass(%s) AND attnum>0 AND NOT attisdropped''', (table,)).fetchall()
        actual = {row['attname']: row['data_type'] for row in rows}
        if not actual:
            missing_tables.append(table)
            continue
        for column, kind in expected.items():
            if column not in actual:
                missing_columns.append(table+'.'+column)
            elif actual[column] != kind:
                incompatible.append(table+'.'+column)
    return {'ready': not (missing_tables or missing_columns or incompatible), 'missing_tables': missing_tables,
            'missing_columns': missing_columns, 'incompatible_columns': incompatible}
