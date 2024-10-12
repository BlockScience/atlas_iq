
from .models import EntityModel, PatternModel, IQueryModel, ResourceHandlerModel
from cachetools import cached, TTLCache

class Repository:
    def __init__(self):
        # Cache with a Time-To-Live of 300 seconds and max size of 100 entries
        self.entity_cache = TTLCache(maxsize=100, ttl=300)

    @cached(cache=lambda self: self.entity_cache)
    def get_entity_by_id(self, entity_id):
        return EntityModel.nodes.get_or_none(entity_id=entity_id)

    def create_entity(self, entity_id, attributes=None):
        entity = EntityModel(entity_id=entity_id, attributes=attributes or {})
        entity.save()
        return entity

    def get_entity_by_id(self, entity_id):
        return EntityModel.nodes.get_or_none(entity_id=entity_id)

    def update_entity_attributes(self, entity_id, new_attributes):
        entity = self.get_entity_by_id(entity_id)
        if entity:
            entity.attributes.update(new_attributes)
            entity.save()
            return entity
        return None

    def delete_entity(self, entity_id):
        entity = self.get_entity_by_id(entity_id)
        if entity:
            entity.delete()

    def create_pattern(self, name):
        pattern = PatternModel(name=name)
        pattern.save()
        return pattern

    def get_pattern_by_name(self, name):
        return PatternModel.nodes.get_or_none(name=name)

    def add_pattern_to_entity(self, entity, pattern):
        entity.patterns.connect(pattern)

    def create_iquery(self, name, target_attribute, conditions=None, status='pending'):
        iquery = IQueryModel(
            name=name,
            target_attribute=target_attribute,
            conditions=conditions or [],
            status=status
        )
        iquery.save()
        return iquery

    def add_iquery_to_entity(self, entity, iquery):
        entity.iqueries.connect(iquery)

    def add_iquery_to_pattern(self, pattern, iquery):
        pattern.iqueries.connect(iquery)

    def create_resource_handler(self, handler_type, config=None):
        handler = ResourceHandlerModel(handler_type=handler_type, config=config or {})
        handler.save()
        return handler

    def add_resource_handler_to_iquery(self, iquery, handler):
        iquery.resource_handlers.connect(handler)

    def batch_create_entities(self, entities_data):
        cypher_query = """
        UNWIND $batch as row
        CREATE (e:EntityModel {entity_id: row.entity_id, attributes: row.attributes})
        RETURN e
        """
        
        results, meta = db.cypher_query(cypher_query, {'batch': entities_data})
        return [EntityModel.inflate(row[0]) for row in results]
    
    def get_resource_handler_by_type(self, handler_type):
        return ResourceHandlerModel.nodes.get_or_none(handler_type=handler_type)

    def create_resource_handler(self, handler_type, config):
        handler = ResourceHandlerModel(handler_type=handler_type, config=config)
        handler.save()
        return handler