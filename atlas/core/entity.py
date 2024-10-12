from ..data.repository import Repository
from typing import Dict, Any
import asyncio

class EntityError(Exception):
    """Custom exception class for Entity-related errors."""
    pass

class Entity:
    """
    Represents an entity in the system.

    This class manages the attributes, patterns, and iQueries associated with an entity.
    It also handles persistence and updates of the entity's state.
    """
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
            if self.attributes:
                self.model.attributes.update(self.attributes)
                self.model.save()
        else:
            self.model = self.repository.create_entity(self.entity_id, self.attributes)

    def initialize_iqueries(self):
        for pattern in self.patterns:
            self.iqueries.extend(pattern.get_iqueries())
            self.repository.add_pattern_to_entity(self.model, pattern.model)

    async def local_update(self, global_state):
        for iquery in self.iqueries:
            try:
                if iquery.check_conditions(self, global_state):
                    new_entity_data = await iquery.execute(self)
                    self.repository.update_entity_attributes(self.entity_id, self.attributes)
                    if new_entity_data:
                        self.generate_new_entities(new_entity_data)
            except Exception as e:
                print(f"Error during local update for Entity '{self.entity_id}': {e}")
    
    def add_pattern(self, pattern):
        """
        Add a new pattern to the entity.

        Args:
            pattern: The pattern to add.

        Raises:
            EntityError: If there's an error adding the pattern.
        """
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
        """
        Add or update an attribute of the entity.

        Args:
            key (str): The attribute key.
            value: The attribute value.

        Raises:
            EntityError: If there's an error adding/updating the attribute.
        """
        try:
            self.attributes[key] = value
            self.repository.update_entity_attributes(self.entity_id, {key: value})
        except Exception as e:
            raise EntityError(f"Failed to add/update attribute '{key}': {e}")

    def get_attribute(self, key):
        """
        Get the value of an entity attribute.

        Args:
            key (str): The attribute key.

        Returns:
            The value of the attribute.

        Raises:
            EntityError: If there's an error retrieving the attribute.
        """
        try:
            return self.attributes.get(key)
        except Exception as e:
            raise EntityError(f"Failed to retrieve attribute '{key}': {e}")

    def remove_pattern(self, pattern):
        """
        Remove a pattern from the entity.

        Args:
            pattern: The pattern to remove.
        """
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
        """
        Remove an attribute from the entity.

        Args:
            key (str): The key of the attribute to remove.
        """
        if key in self.attributes:
            del self.attributes[key]
            self.repository.update_entity_attributes(self.entity_id, self.attributes)
        else:
            print(f"Attribute '{key}' does not exist in Entity '{self.entity_id}'.")
    
    def check_and_generate_new_entities(self, global_state):
        """
        Checks conditions and generates new entities based on iQuery responses.

        Args:
            global_state: The current global state of the system.
        """
        for iquery in self.iqueries:
            if iquery.check_conditions(self, global_state):
                new_entity_data = iquery.execute(self)
                if new_entity_data:
                    new_entity = EntityFactory.create_entity(new_entity_data)
                    self.atlas.register_entity(new_entity)
                    logger.info(f"Generated new entity: {new_entity.entity_id}")

    def generate_new_entities(self, new_entity_data_list):
        for data in new_entity_data_list:
            new_entity = EntityFactory.create_entity(data)
            self.atlas.register_entity(new_entity)

    def update_attributes_from_response(self, response):
        """
        Update entity attributes based on the response from an iQuery.

        Args:
            response (dict): The response data from an iQuery.
        """
        if response and isinstance(response, dict):
            # Update attributes with new data
            self.attributes.update(response)
        else:
            print(f"Invalid response format for entity '{self.entity_id}'.")

    def extract_references_from_attributes(self):
        """
        Extract references from attributes after iQuery execution.

        Returns:
            list: List of new references extracted from attributes.
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
