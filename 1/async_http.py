import asyncio
import json

import aiofiles
import aiohttp
from aiohttp.client_exceptions import (
    ClientConnectionError,
    ClientConnectorDNSError,
    ConnectionTimeoutError,
)

urls = [
    "https://nonexistent.url",
    "https://example.com",
    "https://httpbin.org/status/404",
]


async def fetch_urls(urls: list[str], file_path: str) -> None:
    sem = asyncio.Semaphore(5)
    fetch_tasks = [fetch_url(url, sem) for url in urls]

    for earliest_fetch in asyncio.as_completed(fetch_tasks):
        url, status_code = await earliest_fetch
        await write_to_file(file_path, url, status_code)


async def fetch_url(url: str, sem: asyncio.Semaphore) -> tuple[str, int]:
    async with sem:
        async with aiohttp.ClientSession() as session:
            try:
                r = await session.get(url)
                status_code = r.status
            except ClientConnectorDNSError:
                status_code = 600
            except ConnectionTimeoutError:
                status_code = 601
            except ClientConnectionError:
                status_code = 0
            
            return url, status_code


async def write_to_file(file_path: str, url: str, status_code: int) -> None:
    entry = json.dumps({url: status_code})
    entry_f = f"{entry}\n"
    async with aiofiles.open(file_path, "a", encoding="utf-8") as file:
        await file.write(entry_f)


if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './data/async_http/results.jsonl'))
