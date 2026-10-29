"""Nghiên cứu offline có checkpoint; không tự duyệt/xuất bản và không gọi AI/DB.

python scripts/research_career_videos.py discover
Tôn trọng lỗi429, không tự đổi IP/cookie để vượt giới hạn nguồn.
"""
import argparse,json,re,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from career_library import catalog
from career_videos import public_for
STATE=ROOT/'docs/video-research/progress.json'

def load():
    if STATE.exists():
        state=json.loads(STATE.read_text(encoding='utf8'))
        assert [r['career_id'] for r in state['careers']]==[c.career_id for c in catalog().careers]
        return state
    return {'schema_version':1,'scope':200,'careers':[{'career_id':c.career_id,'name':c.name,'category_id':c.category_id,
        'status':'inherited_verified' if public_for(c.career_id) else 'needs_research','existing_videos':public_for(c.career_id),
        'searches':[],'candidates':[],'decision':None} for c in catalog().careers]}

def save(state):
    STATE.parent.mkdir(parents=True,exist_ok=True);state['updated_at']=datetime.now(timezone.utc).isoformat()
    tmp=STATE.with_suffix('.tmp');tmp.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8');tmp.replace(STATE)

def search(query):
    r=httpx.get('https://www.youtube.com/results',params={'search_query':query},timeout=25,follow_redirects=True)
    if r.status_code==429:return {'query':query,'status':'rate_limited','rows':[]}
    r.raise_for_status();m=re.search(r'var ytInitialData = (\{.*?\});',r.text);rows=[]
    if m:
        def walk(x):
            if isinstance(x,dict):
                if 'videoRenderer' in x:
                    v=x['videoRenderer'];key=v.get('videoId','')
                    if re.fullmatch(r'[A-Za-z0-9_-]{11}',key):
                        rows.append({'video_id':key,'url':'https://www.youtube.com/watch?v='+key,
                            'title':''.join(z.get('text','') for z in v.get('title',{}).get('runs',[])),
                            'channel':''.join(z.get('text','') for z in v.get('ownerText',{}).get('runs',[])),
                            'duration_label':v.get('lengthText',{}).get('simpleText'),
                            'snippet':''.join(z.get('text','') for s in v.get('detailedMetadataSnippets',[]) for z in s.get('snippetText',{}).get('runs',[]))[:650]})
                for a in x.values():walk(a)
            elif isinstance(x,list):
                for a in x:walk(a)
        walk(json.loads(m[1]))
    return {'query':query,'status':'searched' if rows else 'no_results','rows':rows[:8]}

def discover(state):
    todo=[r for r in state['careers'] if not r['existing_videos'] and not r['searches']]
    def work(row):
        query='Nghề '+row['name']+' công việc thực tế'
        try:return row['career_id'],search(query)
        except Exception as e:return row['career_id'],{'query':query,'status':'network_error','error_type':type(e).__name__,'rows':[]}
    byid={r['career_id']:r for r in state['careers']}
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures=[pool.submit(work,r) for r in todo]
        for i,f in enumerate(as_completed(futures),1):
            cid,result=f.result();row=byid[cid];row['searches'].append({k:v for k,v in result.items() if k!='rows'});row['candidates']=result['rows'];row['status']='needs_content_review' if result['rows'] else 'search_failed';save(state)
            if i%20==0 or i==len(todo):print(json.dumps({'searched_this_run':i,'pending_this_run':len(todo)-i,'searched_total':sum(bool(r['searches']) for r in state['careers']),'careers_with_candidates':sum(bool(r['candidates']) for r in state['careers']),'published_added':0}),flush=True)
            if result['status']=='rate_limited':
                print('SOURCE_RATE_LIMIT: stopping new work; no bypass.',flush=True)
                for job in futures:job.cancel()
                break

def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['discover','status']);a=p.parse_args();s=load();save(s)
    if a.mode=='discover':discover(s)
    else:print(json.dumps({'careers':len(s['careers']),'inherited':sum(bool(r['existing_videos']) for r in s['careers']),'searched':sum(bool(r['searches']) for r in s['careers'])}))
if __name__=='__main__':main()
