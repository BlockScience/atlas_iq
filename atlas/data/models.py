# atlas/data/models.py

from neomodel import (
    StructuredNode,
    StringProperty,
    JSONProperty,
    RelationshipTo,
    RelationshipFrom,
    UniqueIdProperty,
)

class ResourceHandlerModel(StructuredNode):
    uid = UniqueIdProperty()
    handler_type = StringProperty(required=True)
    config = JSONProperty(default={})

    # Relationships
    iqueries = RelationshipFrom('IQueryModel', 'USES_HANDLER')

class IQueryModel(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    target_attribute = StringProperty(required=True)
    conditions = JSONProperty(default=[])
    status = StringProperty(default='pending')

    # Relationships
    resource_handlers = RelationshipTo('ResourceHandlerModel', 'USES_HANDLER')
    entity = RelationshipFrom('EntityModel', 'HAS_IQUERY')
    patterns = RelationshipFrom('PatternModel', 'HAS_IQUERY')

class PatternModel(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)

    # Relationships
    iqueries = RelationshipTo('IQueryModel', 'HAS_IQUERY')
    parent_patterns = RelationshipTo('PatternModel', 'INHERITS_FROM')
    entities = RelationshipFrom('EntityModel', 'HAS_PATTERN')

class EntityModel(StructuredNode):
    uid = UniqueIdProperty()
    entity_id = StringProperty(unique_index=True, required=True)
    attributes = JSONProperty(default={})

    # Relationships
    patterns = RelationshipTo('PatternModel', 'HAS_PATTERN')
    iqueries = RelationshipTo('IQueryModel', 'HAS_IQUERY')
