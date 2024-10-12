# atlas/resources/api_handler.py

import aiohttp
import asyncio
from abc import ABC, abstractmethod
import logging
from typing import Any, Optional


logger = logging.getLogger(__name__)

class APIHandler(ABC):
    @abstractmethod
    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        pass

    @abstractmethod
    async def post(self, endpoint: str, data: Dict[str, Any] = None) -> Any:
        pass

class ExternalAPIHandler(APIHandler):
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        try:
            async with self.session.get(url, headers=headers, params=params, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                return data
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error during API GET request: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error during API GET request: {e}")
        return None

    async def post(self, endpoint: str, data: Dict[str, Any] = None) -> Any:
        # Similar implementation for POST requests
        pass

    async def close(self):
        await self.session.close()
