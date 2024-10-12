import aiohttp
import asyncio
import logging
import json
from typing import Any, Dict, Optional
from .llm_handler import LLMHandler
from atlas.utils.config import config
from atlas.core.entity import Entity
from atlas.core.iquery import iQuery
from .llm_handler import LLMHandler
from .response_processor import ResponseProcessor

logger = logging.getLogger(__name__)

from .llm_handler import LLMHandler
from ..data.models import ResourceHandlerModel
from ..utils.config import config
from ..data.repository import Repository

class OpenAIGPTHandler(LLMHandler):
    def __init__(self):
        super().__init__(handler_type='OpenAI', config={'model': config.OPENAI_MODEL})
        self.api_key = config.OPENAI_API_KEY
        self.api_base_url = config.OPENAI_API_BASE_URL
        self.model_name = config.OPENAI_MODEL  # Keep the model name string
        self.session = aiohttp.ClientSession()
        self.semaphore = asyncio.Semaphore(5)
        self.response_processor = ResponseProcessor()
        self._persist_handler()

    def _persist_handler(self):
        repository = Repository()
        existing_handler = repository.get_resource_handler_by_type('OpenAI')
        if existing_handler:
            self.resource_handler_model = existing_handler  # Store the ResourceHandlerModel instance
        else:
            self.resource_handler_model = repository.create_resource_handler('OpenAI', {'model': self.model_name})



    async def execute(self, prompt: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Asynchronously sends the prompt to OpenAI's API and returns the processed response.
        """
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': self.model_name,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 150),
            'n': 1,
            'stop': kwargs.get('stop', None),
        }

        max_retries = kwargs.get('max_retries', 3)
        backoff_factor = kwargs.get('backoff_factor', 0.5)
        logger.debug(f"Starting request with max_retries={max_retries}, backoff_factor={backoff_factor}")
        for attempt in range(max_retries):
            async with self.semaphore:
                try:
                    logger.debug(f"Attempt {attempt + 1}: Sending request to {url}")
                    logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
                    logger.debug(f"Headers: {json.dumps(headers, indent=2)}")
                    async with self.session.post(url, json=payload, headers=headers, timeout=15) as response:
                        response.raise_for_status()
                        data = await response.json()
                        logger.debug(f"Received response: {json.dumps(data, indent=2)}")
                        text_response = data['choices'][0]['message']['content'].strip()
                        processed_data = self.process_response(text_response)
                        logger.debug(f"Processed data: {json.dumps(processed_data, indent=2)}")
                        return processed_data  # Return processed data (dictionary)
                except aiohttp.ClientResponseError as e:
                    if e.status in [429, 500, 502, 503, 504]:
                        delay = backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                        logger.warning(f"Retrying after {delay:.2f} seconds due to {e.status} error")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"Non-retriable HTTP error: {e}")
                        break
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.debug(f"Raw response: {await response.text()}")
                    break
                except Exception as e:
                    logger.exception(f"Unexpected error during LLM request: {e}")
                    break
        logger.error("All attempts failed")
        return None


    def build_prompt(self, entity: Entity, iquery: iQuery) -> str:
        """
        Constructs the prompt based on the entity's attributes and the iQuery's parameters.
        """
        prompt_template = iquery.parameters.get('prompt_template')
        if not prompt_template:
            raise ValueError("Prompt template not found in iQuery parameters.")

        # Advanced context integration
        context = entity.get_context()
        prompt = prompt_template.format(**entity.attributes, context=context)
        return prompt

    def process_response(self, response: str) -> Any:
        """
        Processes and validates the LLM response.
        """
        if self.response_processor.validate_response(response):
            return self.response_processor.extract_information(response)
        else:
            logger.warning("Invalid response received from LLM.")
            return None

    async def close(self):
        await self.session.close()
