import asyncio
from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import AsyncResult

from fastapi import APIRouter

from app.tasks import create_task

api_task_router = APIRouter()


def get_result_sync(result: AsyncResult):
    return result.get()


@api_task_router.post("/run-task/")
async def run_task(param: int):
    result = create_task.delay(param)
    return {"task_id": result.task_id}


@api_task_router.post("/run-task-and-wait/")
async def run_task_and_wait(param: int):
    result: AsyncResult = create_task.delay(param)
    # loop = asyncio.get_event_loop()
    # with ThreadPoolExecutor() as pool:
    #     result_value = await loop.run_in_executor(pool, get_result_sync, result)
    result_value = result.get()
    return result_value
