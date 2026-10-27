"""Request-local connection reuse/timings, never shared identities or transaction state."""
from contextlib import contextmanager
from contextvars import ContextVar
from threading import RLock
from time import perf_counter
import psycopg

current = ContextVar('request_performance',default=None)
class RequestPerformance:
    def __init__(self,reuse=False):
        self.reuse=reuse;self.db=None;self.lock=RLock();self.closed=False;self.values={};self.connections=0;self.provider_calls=0;self.prompt_tokens=0;self.completion_tokens=0;self.pipeline=None
    def close(self):
        with self.lock:
            self.closed=True
            if self.db is not None:self.db.close()
    def header(self):
        return ', '.join([f'{k};dur={v:.1f}' for k,v in self.values.items()]+[f'db_connections;desc="{self.connections}"',f'llm_calls;desc="{self.provider_calls}"',f'llm_input_tokens;desc="{self.prompt_tokens}"',f'llm_output_tokens;desc="{self.completion_tokens}"']+(['ai_pipeline;desc="task41"'] if self.pipeline=='task41' else []))
@contextmanager
def measure(name):
    start=perf_counter()
    try:yield
    finally:
        state=current.get()
        if state is not None:state.values[name]=state.values.get(name,0)+(perf_counter()-start)*1000
class TimingCursor(psycopg.Cursor):
    def execute(self,*args,**kwargs):
        with measure('db_sql'):return super().execute(*args,**kwargs)
