"""Một tác vụ/survey hash, lease PG và ngân sách riêng. Không giữ transaction khi gọi AI."""
import hashlib
import json
import logging
from uuid import uuid4
from fastapi import HTTPException
from .survey import survey_data
from .survey_analysis import ANALYSIS_SCHEMA_VERSION,analysis_trace
from .guest_quota import lock_usage, ensure_unclaimed
from .protection import limit, setting, client_ip

def postgres_connection():
    from .postgres_store import postgres_connection as connect
    return connect()


logger=logging.getLogger(__name__)
LEASE=90


def fingerprint(survey):
    return hashlib.sha256(json.dumps(survey['answers'],ensure_ascii=False).encode()).hexdigest()


def survey_analysis_for_session(session):
    survey=survey_data(session)
    if not survey:return None
    wanted=fingerprint(survey)
    job=session['messages'][0].get('analysis_job',{})
    if job.get('survey_hash')==wanted and job.get('status')=='completed':
        return job.get('result')
    for message in reversed(session['messages']):
        result=message.get('survey_analysis')
        if result and result.get('survey_hash')==wanted:return result
    return None


def analysis_for_session(session):
    from .profile_proposals import merge
    return merge(session,survey_analysis_for_session(session))


def state(session):
    survey=survey_data(session)
    result=analysis_for_session(session)
    request_id=survey['analysis_request_id'] if survey else None
    job=session['messages'][0].get('analysis_job',{}) if session['messages'] else {}
    trace={'schema_version':ANALYSIS_SCHEMA_VERSION,'trace_id':job.get('trace_id')}
    if result:return {'status':'completed','ready':True,'result':result,'chat_quota_charge':0,'request_id':request_id,**trace}
    if not survey:return {'status':'pending','ready':False,'chat_quota_charge':0}
    job=session['messages'][0].get('analysis_job',{})
    if job.get('survey_hash')!=fingerprint(survey):job={}
    import time
    if job.get('status')=='processing' and job.get('lease_until',0)<=time.time():
        return {'status':'failed','ready':True,'error_code':'interrupted','chat_quota_charge':0,'request_id':request_id,**trace}
    return {'status':job.get('status','pending'),'ready':True,'error_code':job.get('error_code'),
            'chat_quota_charge':0,'request_id':request_id,**trace}


def locked_session(db,uid,sid):
    # Cùng thứ tự usage -> session như claim/quota. UID đến từ backend auth.
    lock_usage(db,uid);ensure_unclaimed(db,uid)
    for table in ('advisor_sessions','advisor_temporary_sessions'):
        expiry=' AND expires_at>NOW()' if table.endswith('temporary_sessions') else ''
        row=db.execute(f'SELECT messages FROM {table} WHERE owner=%s AND id=%s{expiry} FOR UPDATE',(uid,sid)).fetchone()
        if row:return table,{'id':sid,'messages':json.loads(row['messages'])}
    raise HTTPException(404,'Không tìm thấy cuộc trò chuyện của bạn.')


def write(db,table,uid,session):
    db.execute(f'UPDATE {table} SET messages=%s WHERE owner=%s AND id=%s',
               (json.dumps(session['messages'],ensure_ascii=False),uid,session['id']))


def claim(uid,sid,ip,retry=False,request_id=None):
    with postgres_connection() as db:
        table,session=locked_session(db,uid,sid);survey=survey_data(session)
        if not survey:raise HTTPException(409,'Hoàn thành 5 câu khảo sát trước khi phân tích.')
        if request_id is not None and request_id!=survey['analysis_request_id']:
            raise HTTPException(409,'Yêu cầu phân tích không khớp khảo sát của cuộc trò chuyện.')
        if survey_analysis_for_session(session):return state(session),None,None
        now=float(db.execute('SELECT EXTRACT(EPOCH FROM NOW()) AS ts').fetchone()['ts'])
        job=session['messages'][0].get('analysis_job',{})
        same=job.get('survey_hash')==fingerprint(survey)
        if same and job.get('status')=='processing' and job.get('lease_until',0)>now:
            return state(session),None,None
        if same and job.get('status')=='failed' and not retry:return state(session),None,None
        import os
        if not os.getenv('DEEPSEEK_API_KEY','').strip():
            session['messages'][0]['analysis_job']={'status':'failed','survey_hash':fingerprint(survey),
                'survey_id':survey['analysis_request_id'],'error_code':'not_configured','attempts':job.get('attempts',0),'version':1}
            write(db,table,uid,session)
            return state(session),None,None
        # Chỉ tính ngân sách khi một attempt mới thực sự được giữ; cached/invalid/parallel không tính.
        limit(db,'analysis:ip:day',ip,setting('ANALYSIS_IP_PER_DAY',30),86400)
        limit(db,'analysis:uid:day',uid,setting('ANALYSIS_USER_PER_DAY',6),86400)
        limit(db,'analysis:uid:minute',uid,setting('ANALYSIS_USER_PER_MINUTE',2),60)
        attempt=str(uuid4())
        session['messages'][0]['analysis_job']={'status':'processing','survey_hash':fingerprint(survey),
            'survey_id':survey['analysis_request_id'],'attempt_id':attempt,'lease_until':now+LEASE,
            'attempts':job.get('attempts',0)+1 if same else 1,'version':1,
            'trace_id':uuid4().hex,'schema_version':ANALYSIS_SCHEMA_VERSION}
        write(db,table,uid,session)
        return state(session),attempt,session


def finish(uid,sid,attempt,survey_hash,result=None,error_code=None):
    with postgres_connection() as db:
        table,session=locked_session(db,uid,sid)
        job=session['messages'][0].get('analysis_job',{})
        if job.get('attempt_id')!=attempt or job.get('survey_hash')!=survey_hash:
            return state(session)  # Worker cũ không ghi đè attempt mới.
        survey=survey_data(session)
        if not survey or fingerprint(survey)!=survey_hash:raise HTTPException(409,'Khảo sát đã thay đổi.')
        job.update(status='completed' if result else 'failed',error_code=error_code)
        job.pop('lease_until',None)
        if result:job['result']=result
        write(db,table,uid,session)
        return state(session)


async def execute(request,user,store,sid,retry=False,request_id=None):
    import asyncio,os
    from .postgres_adapter import PostgresConversationStore
    if not isinstance(store,PostgresConversationStore):raise HTTPException(503,'Phân tích tự động cần PostgreSQL.')
    current,attempt,session=await asyncio.to_thread(claim,user['uid'],sid,client_ip(request),retry,request_id)
    if not attempt:return current
    survey=survey_data(session)
    trace_id=session['messages'][0]['analysis_job']['trace_id']
    trace_token=analysis_trace.set(trace_id)
    try:
        from .survey_analysis import generate_analysis
        result=await generate_analysis(survey,sid)
    except BaseException as error:
        from .survey_analysis import AnalysisValidationError
        code=error.code if isinstance(error,AnalysisValidationError) else type(error).__name__
        # Chỉ log loại lỗi, không prompt/response/survey/UID/connection string.
        logger.warning('survey_analysis_failed error_code=%s error_type=%s schema_version=%s trace_id=%s',
                       code,type(error).__name__,ANALYSIS_SCHEMA_VERSION,trace_id)
        await asyncio.shield(asyncio.to_thread(finish,user['uid'],sid,attempt,fingerprint(survey),None,code))
        if isinstance(error,asyncio.CancelledError):raise
        return {'status':'failed','ready':True,'error_code':'invalid_analysis' if isinstance(error,AnalysisValidationError) else 'provider_unavailable',
                'chat_quota_charge':0,'request_id':survey['analysis_request_id'],
                'schema_version':ANALYSIS_SCHEMA_VERSION,'trace_id':trace_id}
    finally:analysis_trace.reset(trace_token)
    return await asyncio.to_thread(finish,user['uid'],sid,attempt,fingerprint(survey),result)


def attach_analysis(state):
    result=analysis_for_session(state['session'])
    return {'survey_insights':{'summary':result['summary'],'clarification_questions':result.get('clarification_questions',[])[:3]} if result else None,
            'survey_analysis':None,'analysis_status':'stored' if result else 'not_requested'}


def pending(uid,sid):
    with postgres_connection() as db:
        table,session=locked_session(db,uid,sid)
        survey=survey_data(session)
        if not survey:return
        job=session['messages'][0].get('analysis_job',{})
        if job.get('survey_hash')==fingerprint(survey) or analysis_for_session(session):return
        session['messages'][0]['analysis_job']={'status':'pending','survey_hash':fingerprint(survey),
            'survey_id':survey['analysis_request_id'],'attempts':0,'version':1}
        write(db,table,uid,session)
