"""Compatibility response shape, with the same Task4.1 answer engine as chat."""
from langgraph.graph import END, START, StateGraph
from advisor.graph import AdvisorState, answer_graph

class AdviceState(AdvisorState,total=False):
    question:str
    context:str
    answer:str
    sources:list
    search_status:str
    pipeline:str

async def ask_deepseek(state):
    # uid/session are supplied by the verified quota wrapper, never the client.
    result=await answer_graph.ainvoke({**state,'message':state['question'],
        'scene_context':state.get('context',''),'confirmed_profile':[],
        'confirmed_profile_access':False})
    reply=result['reply']
    return {'answer':reply['answer'],'reply':reply,'sources':reply.get('sources',[]),
            'search_status':reply.get('search_status','not_needed'),'pipeline':'task41'}

builder=StateGraph(AdviceState)
builder.add_node('task41_answer',ask_deepseek)
builder.add_edge(START,'task41_answer');builder.add_edge('task41_answer',END)
advice_graph=builder.compile()
