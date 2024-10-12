# atlas/resources/database_handler.py

import asyncpg
import logging
from abc import ABC, abstractmethod
from typing import Any, List

logger = logging.getLogger(__name__)

class DatabaseHandler(ABC):
    @abstractmethod
    async def fetch(self, query: str, *args) -> List[Any]:
        pass

    @abstractmethod
    async def execute(self, query: str, *args) -> None:
        pass

class AsyncPGDatabaseHandler(DatabaseHandler):
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def initialize(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn, min_size=1, max_size=10)

    async def fetch(self, query: str, *args) -> List[Any]:
        if not self.pool:
            await self.initialize()
        try:
            async with self.pool.acquire() as connection:
                result = await connection.fetch(query, *args)
                return result
        except Exception as e:
            logger.exception(f"Error fetching from database: {e}")
            return []

    async def execute(self, query: str, *args) -> None:
        if not self.pool:
            await self.initialize()
        try:
            async with self.pool.acquire() as connection:
                await connection.execute(query, *args)
        except Exception as e:
            logger.exception(f"Error executing database command: {e}")

    async def close(self):
        if self.pool:
            await self.pool.close()
