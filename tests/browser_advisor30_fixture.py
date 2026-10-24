"""Chỉ loopback tests; không nằm trong artifact Vercel. Không gọi provider thật."""
import json
import httpx

def install():
    import advisor.graph as graph
    import advisor.routes as routes
    from test_advisor30_profile import RAW
    graph.demo_mode=lambda:False
    routes.demo_mode=lambda:False
    async def fake(payload,**kwargs):
        system=payload['messages'][0]['content']
        if 'Phân tích CÙNG LÚC' in system:text=json.dumps(RAW,ensure_ascii=False)
        elif 'bộ nén ngữ cảnh' in system:text=json.dumps({'profile':{'interests':[],'strengths':[],'growth_skills':[],'careers':[]},'summary':'Ngữ cảnh kiểm thử, không phải phân tích thật.'})
        else:text='**GIẢ LẬP KIỂM THỬ · chưa gọi DeepSeek.** Bạn có thể tìm hiểu công việc, kỹ năng và thử trải nghiệm an toàn. Khảo sát không phải đánh giá năng lực.'
        return httpx.Response(200,json={'choices':[{'message':{'content':text},'finish_reason':'stop'}]})
    graph.post_completion=fake
