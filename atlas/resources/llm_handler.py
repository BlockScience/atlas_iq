from abc import ABC, abstractmethod
from ..data.repository import Repository
from ..data.models import ResourceHandlerModel
from typing import Any, Optional

class LLMHandler(ABC):
    def __init__(self, handler_type='LLM', config=None):
        self.repository = Repository()
        self.handler_type = handler_type
        self.config = config or {}

class LLMHandler(ABC):
    def __init__(self, handler_type='LLM', config=None):
        self.repository = Repository()
        self.handler_type = handler_type
        self.config = config or {}
        self.model = None  # This will be set in _persist_handler

    @abstractmethod
    def _persist_handler(self):
        pass

    @abstractmethod
    async def execute(self, prompt: str, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def build_prompt(self, entity: 'Entity', iquery: 'iQuery') -> str:
        pass

    @abstractmethod
    def process_response(self, response: str) -> Any:
        pass
