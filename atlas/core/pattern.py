from ..data.repository import Repository
import logging

logger = logging.getLogger(__name__)

class PatternConsistencyError(Exception):
    pass

class Pattern:
    def __init__(self, name, iqueries=None, parent_patterns=None):
        self.repository = Repository()
        self.name = name
        self.iqueries = iqueries or []
        self.parent_patterns = parent_patterns or []
        self._persist_pattern()

    def _persist_pattern(self):
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
        inherited_iqueries = []
        for parent in self.parent_patterns:
            inherited_iqueries.extend(parent.get_iqueries())
        return inherited_iqueries + self.iqueries

    def add_iquery(self, iquery):
        if iquery in self.iqueries:
            print(f"iQuery '{iquery.name}' already exists in Pattern '{self.name}'.")
            return
        self.iqueries.append(iquery)
        self.repository.add_iquery_to_pattern(self.model, iquery.model)

    def inherit_from(self, parent_pattern):
        if parent_pattern in self.parent_patterns:
            print(f"Pattern '{parent_pattern.name}' is already a parent of Pattern '{self.name}'.")
            return
        self.parent_patterns.append(parent_pattern)
        self.model.parent_patterns.connect(parent_pattern.model)

    def validate_consistency(self):
        visited = set()
        def dfs(pattern):
            if pattern in visited:
                raise PatternConsistencyError(f"Circular inheritance detected in pattern '{pattern.name}'")
            visited.add(pattern)
            for parent in pattern.parent_patterns:
                dfs(parent)
        dfs(self)
        logger.info(f"Pattern '{self.name}' passed consistency validation.")