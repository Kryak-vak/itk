"""
Pickling issue needs fixing
"""


import asyncio
import time
from collections.abc import Callable
from datetime import timedelta
from functools import wraps
from multiprocessing import Process, Queue
from typing import cast

from redis import Redis

redis_cli = Redis(host='localhost', port=6379, decode_responses=True)


class FuncLock:
    def __init__(self, redis_cli: Redis, func_key: str, func_max_time: timedelta) -> None:
        self.redis_cli = redis_cli
        self.func_key = func_key
        self.lock_acquired = False

        self.default_exp = 2
        self.lock_release_exp = self.default_exp + int(func_max_time.total_seconds() // 60)
    
    def __enter__(self):
        while True:
            cur_timestr = self._get_timestr()

            if self.redis_cli.set(self.func_key, cur_timestr, nx=True):
                break

            existing_timestr = cast(str, self.redis_cli.get(self.func_key))
            if self._is_expired(existing_timestr):
                old_timestr = cast(
                    tuple[int, int],
                    self.redis_cli.set(self.func_key, cur_timestr, get=True)
                )

                if self._is_expired(old_timestr):
                    break
            
            time.sleep(0.1)

        self.lock_acquired = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.redis_cli.delete(self.func_key)
        self.lock_acquired = False

    def _get_timestr(self, exp_mins: int | None = None) -> str:
        exp_mins = exp_mins if exp_mins is not None else self.lock_release_exp

        cur_time = self._get_time()
        exp_seconds = cur_time[0] + exp_mins * 60
        return f"{exp_seconds},{cur_time[1]}"
    
    def _get_time(self) -> tuple[int, int]:
        return cast(tuple[int, int], self.redis_cli.time())

    def _is_expired(self, timespec: str | tuple[int, int]) -> bool:
        if isinstance(timespec, str):
            seconds, milliseconds = map(int, timespec.split(","))
        else:
            seconds, milliseconds = timespec

        cur_seconds, cur_milliseconds = self._get_time()

        if seconds < cur_seconds:
            return True
        elif seconds == cur_seconds:
            if milliseconds < cur_milliseconds:
                return True
        
        return False


def worker(q: Queue, func: Callable, args: tuple, kwargs: dict):
    try:
        result = func(*args, **kwargs)
        q.put(("result", result))
    except Exception as e:
        q.put(("error", e))


def single(
        func: Callable | None = None, *,
        max_processing_time: timedelta = timedelta(seconds=30)
    ):
    def lock(func):
        prefix = "lock_"
        func_key = f"{prefix}{func.__name__}"
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            q = Queue(maxsize=1)
            func_process = Process(target=worker, args=(q, func, args, kwargs))

            with FuncLock(redis_cli, func_key, max_processing_time):
                func_process.start()
                func_process.join(timeout=max_processing_time.total_seconds())
                if func_process.is_alive():
                    func_process.terminate()
                    raise TimeoutError
            
            out_type, out_value = q.get(timeout=1)
            if out_type == "result":
                result = out_value
            else:
                raise out_value
            
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with FuncLock(redis_cli, func_key, max_processing_time):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=max_processing_time.total_seconds()
                )
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    if func is None:
        return lock
    else:
        return lock(func)