import time
import random
import json
import logging
import asyncio
from functools import reduce
from operator import and_, or_
from typing import Any

from ..data.repository import Repository
from ..data.models import IQueryModel, ResourceHandlerModel

class iQuery:
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2  # Exponential backoff factor
    VALID_STATUSES = {'pending', 'executing', 'completed', 'failed', 'retrying'}
    
    def __init__(self, name, target_attribute, resource_handlers, conditions=None):
        self.repository = Repository()
        self.name = name
        self.target_attribute = target_attribute
        self.resource_handlers = resource_handlers  # List of handler instances
        self.resource_handler_models = [handler.resource_handler_model for handler in resource_handlers]  # Extract models
        self.conditions = conditions or []
        self.status = 'pending'
        self.retry_count = 0
        self._persist_iquery()

    def _persist_iquery(self):
        existing_iquery = IQueryModel.nodes.get_or_none(name=self.name)
        if existing_iquery:
            self.model = existing_iquery
        else:
            self.model = self.repository.create_iquery(
                self.name,
                self.target_attribute,
                self.conditions,
                self.status
            )
        for handler_model in self.resource_handler_models:
            self.repository.add_resource_handler_to_iquery(self.model, handler_model)

    def check_conditions(self, entity, global_state):
        if not self.conditions:
            return True
        return self.conditions.evaluate(entity, global_state)

    async def execute(self, entity):
        logging.info(f"Executing IQuery '{self.name}' for entity {entity}")
        self.status = 'executing'
        self.model.status = self.status
        self.model.save()
        handlers = self.resource_handlers.copy()
        while handlers and self.retry_count <= self.MAX_RETRIES:
            handler = handlers.pop(0)
            try:
                query = self.build_query(entity)
                logging.debug(f"Built query: {query}")
                response = await handler.execute(query)
                logging.debug(f"Received response: {response}")
                if response:
                    # Use the processed response directly
                    attribute_value, new_entity_data = self.process_response(response)
                    entity.add_attribute(self.target_attribute, attribute_value)
                    self.status = 'completed'
                    self.model.status = self.status
                    self.model.save()
                    logging.info(f"IQuery '{self.name}' completed successfully")
                    return attribute_value
            except Exception as e:
                logging.error(f"Error with handler '{handler}': {str(e)}", exc_info=True)
                self.retry_count += 1
                if self.retry_count > self.MAX_RETRIES:
                    if handlers:
                        logging.warning(f"Falling back to next handler for IQuery '{self.name}'")
                        self.status = 'retrying'
                        self.retry_count = 0  # Reset for next handler
                        continue
                    else:
                        logging.error(f"No more handlers to try. Marking IQuery '{self.name}' as failed")
                        self.status = 'failed'
                        self.model.status = self.status
                        self.model.save()
                        return
                backoff_time = self.BACKOFF_FACTOR ** self.retry_count + random.uniform(0, 1)
                logging.info(f"Retrying with handler '{handler}' in {backoff_time:.2f} seconds...")
                self.status = 'retrying'
                self.model.status = self.status
                self.model.save()
                await asyncio.sleep(backoff_time)
            self.status = 'failed'
            self.model.status = self.status
            self.model.save()
            logging.error(f"IQuery '{self.name}' failed after all retries")

    def build_query(self, entity):
        # Custom implementation as needed
        return f"Provide {self.target_attribute} for {entity.entity_id}"

    def update_status(self, new_status):
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{new_status}' for iQuery.")
        self.status = new_status
        self.model.status = self.status
        self.model.save()
        
    def process_response(self, response):
        # Example processing logic
        # Assume response is a dictionary with keys 'attribute_value' and 'new_entities'
        attribute_value = response.get('attribute_value')
        new_entities = response.get('new_entities', [])
        return attribute_value, new_entities
    

