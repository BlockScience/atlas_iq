from ..data.repository import Repository
from .entity import Entity
import logging

logger = logging.getLogger(__name__)


class PatternConsistencyError(Exception):
    """Custom exception for consistency-related issues in Patterns."""
    pass

class Pattern(Entity):
    def __init__(self, name, iqueries=None, parent_patterns=None, attributes=None):
        """
        Patterns now inherit from Entity, enabling them to have iQueries, attributes,
        and self-generation behavior.
        """
        super().__init__(entity_id=name, patterns=parent_patterns, attributes=attributes)
        self.name = name  # Add this line to set the name attribute
        self.iqueries = iqueries or []
        self.parent_patterns = parent_patterns or []
        self._persist_pattern()

    def _persist_pattern(self):
        """
        Persists the pattern in the repository.
        """
        existing_pattern = self.repository.get_pattern_by_name(self.name)
        if existing_pattern:
            self.model = existing_pattern
        else:
            self.model = self.repository.create_pattern(self.name)
        for iquery in self.iqueries:
            self.repository.add_iquery_to_pattern(self.model, iquery.model)
        for parent_pattern in self.parent_patterns:
            self.model.parent_patterns.connect(parent_pattern.model)

    def get_iqueries(self):
        """
        Returns all iQueries, including inherited ones from parent patterns.
        """
        inherited_iqueries = []
        for parent in self.parent_patterns:
            inherited_iqueries.extend(parent.get_iqueries())
        return inherited_iqueries + self.iqueries

    def add_iquery(self, iquery):
        """
        Adds an iQuery to the pattern.
        """
        if iquery in self.iqueries:
            print(f"iQuery '{iquery.name}' already exists in Pattern '{self.name}'.")
            return
        self.iqueries.append(iquery)
        self.repository.add_iquery_to_pattern(self.model, iquery.model)

    def inherit_from(self, parent_pattern):
        """
        Allows the pattern to inherit from a parent pattern.
        """
        if parent_pattern in self.parent_patterns:
            print(f"Pattern '{parent_pattern.name}' is already a parent of Pattern '{self.name}'.")
            return
        self.parent_patterns.append(parent_pattern)
        self.model.parent_patterns.connect(parent_pattern.model)

    def validate_consistency(self):
        """
        Checks for conflicting iQueries or circular inheritance.
        """
        visited = set()
        def dfs(pattern):
            if pattern in visited:
                raise PatternConsistencyError(f"Circular inheritance detected in pattern '{pattern.name}'")
            visited.add(pattern)
            for parent in pattern.parent_patterns:
                dfs(parent)
        dfs(self)
        logger.info(f"Pattern '{self.name}' passed consistency validation.")

    async def generate_new_pattern(self, global_state):
        """
        Generates new patterns based on existing patterns and global state.
        """
        new_iqueries = self.get_iqueries()
        new_pattern_name = f"{self.name}_variant"
        new_pattern = Pattern(name=new_pattern_name, iqueries=new_iqueries, parent_patterns=[self])
        logger.info(f"Generated new pattern: {new_pattern.name}")
        return new_pattern

    def self_modify(self, global_state):
        """
        Logic for self-modification based on global state or conditions.
        """
        # Placeholder for modification logic based on global state
        pass

    async def local_update(self, global_state):
        """
        Updates the pattern locally and handles self-modification and generation of new patterns.
        """
        await super().local_update(global_state)
        self.self_modify(global_state)
        await self.generate_new_pattern(global_state)

