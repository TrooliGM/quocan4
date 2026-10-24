"""Chỉ loopback tests; không nằm trong artifact Vercel. Không gọi provider thật."""
import json
import httpx
EVIDENCE={'analysis_calls':0,'main_calls':0,'last_context_has_profile':False,'timeout_attempts':0}

def install():
    import advisor.graph as graph
    import advisor.routes as routes
    from test_advisor30_profile import RAW
    graph.demo_mode=lambda:False
    routes.demo_mode=lambda:False
    async def fake(payload,**kwargs):
        system=payload['messages'][0]['content']
        if 'Phân tích CÙNG LÚC' in system:
            EVIDENCE['analysis_calls']+=1;text=json.dumps(RAW,ensure_ascii=False)
        elif 'bộ nén ngữ cảnh' in system:text=json.dumps({'profile':{'interests':[],'strengths':[],'growth_skills':[],'careers':[]},'summary':'Ngữ cảnh kiểm thử, không phải phân tích thật.'})
        else:
            EVIDENCE['main_calls']+=1
            for m in payload['messages']:
                if m['role']=='system' and m['content'].startswith('Dữ liệu ngữ cảnh'):
                    context=json.loads(m['content'].split('\n',1)[1]);EVIDENCE['last_context_has_profile']=bool(context.get('confirmed_profile'))
            if payload['messages'][-1]['content']=='Kiểm thử timeout':
                EVIDENCE['timeout_attempts']+=1
                if EVIDENCE['timeout_attempts']==1:raise httpx.ReadTimeout('fixture timeout')
            text='**GIẢ LẬP KIỂM THỬ · chưa gọi DeepSeek.** Bạn có thể tìm hiểu công việc, kỹ năng và thử trải nghiệm an toàn. Khảo sát không phải đánh giá năng lực.'
        return httpx.Response(200,json={'choices':[{'message':{'content':text},'finish_reason':'stop'}]})
    graph.post_completion=fake
    from browser_fixture import app
    @app.get('/__qa/advisor30')
    def evidence():return EVIDENCE
