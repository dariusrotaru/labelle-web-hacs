from __future__ import annotations

import asyncio

import aiohttp


class LabelleApiClient:

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")

    async def health(self) -> dict:
        async with asyncio.timeout(10):
            async with self._session.get(f"{self._base_url}/api/health") as response:
                response.raise_for_status()
                return await response.json()