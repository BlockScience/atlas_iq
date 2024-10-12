from ..data.repository import Repository
from typing import Dict, Any
import asyncio

class EntityError(Exception):
    """Custom exception class for Entity-related errors."""
    pass

class Entity:
    def __init__(self, entity_id, patterns=None, attributes=None):
        from .atlas import ATLAS  
        self.repository = Repository()
        self.atlas = ATLAS()
        self.entity_id = entity_id
        self.patterns = patterns or []
        self.iqueries = []
        self.attributes = attributes or {}
        self.references = self.attributes.get('references', [])
        self._persist_entity()
        self.initialize_iqueries()
        self.atlas.register_entity(self)


    def _persist_entity(self):
        existing_entity = self.repository.get_entity_by_id(self.entity_id)
        if existing_entity:
            self.model = existing_entity
            # Update attributes if necessary
            if self.attributes:
                self.model.attributes.update(self.attributes)
                self.model.save()
        else:
            self.model = self.repository.create_entity(self.entity_id, self.attributes)

    def initialize_iqueries(self):
        try:
            for pattern in self.patterns:
                self.iqueries.extend(pattern.get_iqueries())
                self.repository.add_pattern_to_entity(self.model, pattern.model)
            for iquery in self.iqueries:
                self.repository.add_iquery_to_entity(self.model, iquery.model)
        except Exception as e:
            raise EntityError(f"Failed to initialize iQueries: {e}")

    async def local_update(self, global_state):
        for iquery in self.iqueries:
            try:
                if iquery.check_conditions(self, global_state):
                    response = await iquery.execute(self)
                    self.update_attributes_from_response(response)
                    self.repository.update_entity_attributes(self.entity_id, self.attributes)
                    new_references = self.extract_references_from_attributes()
                    self.references.extend(new_references)
            except Exception as e:
                logger.error(f"Error during local update for Entity '{self.entity_id}': {e}")


    def add_pattern(self, pattern):
        if pattern in self.patterns:
            print(f"Pattern '{pattern.name}' is already assigned to Entity '{self.entity_id}'.")
            return
        self.patterns.append(pattern)
        try:
            self.iqueries.extend(pattern.get_iqueries())
            self.repository.add_pattern_to_entity(self.model, pattern.model)
        except Exception as e:
            raise EntityError(f"Failed to add Pattern '{pattern.name}': {e}")

    def add_attribute(self, key, value):
        try:
            self.attributes[key] = value
            self.repository.update_entity_attributes(self.entity_id, {key: value})
        except Exception as e:
            raise EntityError(f"Failed to add/update attribute '{key}': {e}")

    def get_attribute(self, key):
        try:
            return self.attributes.get(key)
        except Exception as e:
            raise EntityError(f"Failed to retrieve attribute '{key}': {e}")

    def remove_pattern(self, pattern):
        if pattern not in self.patterns:
            print(f"Pattern '{pattern.name}' is not assigned to Entity '{self.entity_id}'.")
            return
        self.patterns.remove(pattern)
        # Remove the relationship in the repository
        self.model.patterns.disconnect(pattern.model)
        # Reinitialize iQueries
        self.iqueries = []
        self.initialize_iqueries()

    def remove_attribute(self, key):
        if key in self.attributes:
            del self.attributes[key]
            self.repository.update_entity_attributes(self.entity_id, self.attributes)
        else:
            print(f"Attribute '{key}' does not exist in Entity '{self.entity_id}'.")
    
    def check_and_generate_new_entities(self, global_state):
        """
        Checks conditions and generates new entities based on iQuery responses.
        """
        for iquery in self.iqueries:
            if iquery.check_conditions(self, global_state):
                new_entity_data = iquery.execute(self)
                if new_entity_data:
                    new_entity = EntityFactory.create_entity(new_entity_data)  # Use an Entity Factory for consistency
                    self.atlas.register_entity(new_entity)
                    logger.info(f"Generated new entity: {new_entity.entity_id}")


    async def local_update(self, global_state):
        for iquery in self.iqueries:
            try:
                if iquery.check_conditions(self, global_state):
                    new_entity_data = await iquery.execute(self)
                    # Update the entity's attributes in the repository
                    self.repository.update_entity_attributes(self.entity_id, self.attributes)
                    if new_entity_data:
                        self.generate_new_entities(new_entity_data)
            except Exception as e:
                print(f"Error during local update for Entity '{self.entity_id}': {e}")
    
    def generate_new_entities(self, new_entity_data_list):
        for data in new_entity_data_list:
            new_entity = EntityFactory.create_entity(data)
            self.atlas.register_entity(new_entity)
            logger.info(f"Generated new entity: {new_entity.entity_id}")
    
    def update_attributes_from_response(self, response):
        """
        Update entity attributes based on the response from an iQuery.
        """
        if response and isinstance(response, dict):
            # Update attributes with new data
            self.attributes.update(response)
        else:
            print(f"Invalid response format for entity '{self.entity_id}'.")

def extract_references_from_attributes(self):
    """
    Extract references from attributes after iQuery execution.
    """
    # Assuming the response includes a 'references' field with new references
    new_references = self.attributes.get('references', [])
    # Ensure references are unique
    return [ref for ref in new_references if ref not in self.references]



class EntityFactory:
    """
    A factory to manage the creation of new entities.
    This ensures uniform creation logic and avoids inconsistencies.
    """
    @staticmethod
    def create_entity(entity_data):
        entity_id = entity_data['entity_id']
        patterns = entity_data.get('patterns', [])
        attributes = entity_data.get('attributes', {})
        return Entity(entity_id=entity_id, patterns=patterns, attributes=attributes)
