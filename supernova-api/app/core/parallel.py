import asyncio
from asyncio import AbstractEventLoop, Future
from concurrent.futures.thread import ThreadPoolExecutor

from fastapi import Request

"""

https://github.com/tiangolo/fastapi/issues/2574

Write something down here
from starlette.concurrency import run_in_threadpool

def synchronous_code_than_could_be_long_blocking(arg:int)-> int:
    print(arg)
    sleep(10) # any long synchronous call ( like SQLAlchemy call )
    return arg

@app.post("/reports/")
async def submit_report(request: Request):
    body = await request.body()
    rst = await run_in_threadpool(synchronous_code_than_could_be_long_blocking, 1378473)
"""

"""
something for the executor
"""


async def get_process_executor(request: Request):
    return request.app.state.process_executor


class AshleyMadison:
    def __init__(self, request: Request):
        self.executor: ThreadPoolExecutor = request.app.state.executor
        self.main_engine = request.app.state.main_engine

    async def __call__(self, func, *args):
        loop: AbstractEventLoop = asyncio.get_event_loop()
        try:
            conn = self.main_engine.connect()
            future: Future = loop.run_in_executor(self.executor, func, conn, *args)
            await future
            result = future.result()
            if conn.in_transaction():
                conn.commit()
        except:
            if conn.in_transaction():
                conn.rollback()
        finally:
            conn.close()
        return result
