import asyncio
import json
from collections.abc import AsyncGenerator

import aiofiles
import aiohttp
from aiohttp.client_exceptions import (
    ClientConnectionError,
    ClientConnectorDNSError,
    ConnectionTimeoutError,
    ContentTypeError,
)


async def fetch_urls(urls_file_path: str, result_file_path: str) -> None:
    fetch_queue = asyncio.Queue(maxsize=5)
    tasks: list[asyncio.Task] = []
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(3)) as session:
        for _ in range(2):
            task = asyncio.create_task(worker(fetch_queue, session, result_file_path))
            tasks.append(task)

        async for url in read_url(urls_file_path):
            await fetch_queue.put(url)
        
        await fetch_queue.join()

        for task in tasks:
            task.cancel()
    
        await asyncio.gather(*tasks, return_exceptions=True)


async def worker(queue: asyncio.Queue, session: aiohttp.ClientSession, file_path: str):
    while True:
        url = await queue.get()
        
        try:
            url, data = await fetch_url(url, session)
            await write_to_file(file_path, url, data)
        except Exception as e:
            await write_to_file(file_path, url, {"status": -1, "error": str(e)})
        finally:
            queue.task_done()


async def fetch_url(url: str, session: aiohttp.ClientSession) -> tuple[str, dict]:
    try:
        r = await session.get(url)
        data = await r.json()
    except (
        ClientConnectorDNSError, ConnectionTimeoutError, 
        ContentTypeError, ClientConnectionError, asyncio.TimeoutError
    ) as e:
        data = {"status": 0, "error": str(e)}
    
    return url, data


async def write_to_file(file_path: str, url: str, data: dict) -> None:
    entry = json.dumps(
        {
            "url": url,
            "content": data
        }
    )
    entry_f = f"{entry}\n"
    async with aiofiles.open(file_path, "a", encoding="utf-8") as file:
        await file.write(entry_f)


async def read_url(file_path: str) -> AsyncGenerator[str, str]:
    async with aiofiles.open(file_path, "r") as file:
        async for line in file:
            yield line.strip()


if __name__ == '__main__':
    asyncio.run(
        fetch_urls(
            './data/async_http_advanced/urls.txt',
            './data/async_http_advanced/results.jsonl'
        )
    )
