from abc import ABC, abstractmethod
import operator

class Condition(ABC):
    @abstractmethod
    def evaluate(self, entity, global_state):
        pass

    def __and__(self, other):
        return CompositeCondition(operator.and_, [self, other])

    def __or__(self, other):
        return CompositeCondition(operator.or_, [self, other])

    def __invert__(self):
        return CompositeCondition(operator.not_, [self])

class AttributeCondition(Condition):
    def __init__(self, attribute_name, expected_value, comparison=operator.eq):
        self.attribute_name = attribute_name
        self.expected_value = expected_value
        self.comparison = comparison

    def evaluate(self, entity, global_state):
        actual_value = entity.get_attribute(self.attribute_name)
        return self.comparison(actual_value, self.expected_value)

class GlobalCondition(Condition):
    def __init__(self, global_key, expected_value, comparison=operator.eq):
        self.global_key = global_key
        self.expected_value = expected_value
        self.comparison = comparison

    def evaluate(self, entity, global_state):
        actual_value = global_state.get(self.global_key)
        return self.comparison(actual_value, self.expected_value)

class CompositeCondition(Condition):
    def __init__(self, operator_func, conditions):
        self.operator_func = operator_func
        self.conditions = conditions

    def evaluate(self, entity, global_state):
        results = [cond.evaluate(entity, global_state) for cond in self.conditions]
        return self.operator_func(*results)
