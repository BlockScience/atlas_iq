from abc import ABC, abstractmethod
import operator

class Condition(ABC):
    """
    An abstract base class representing a condition.

    This class defines the interface for all condition classes and provides
    logical operation methods (__and__, __or__, __invert__) for combining conditions.
    """

    @abstractmethod
    def evaluate(self, entity, global_state):
        """
        Evaluate the condition for a given entity and global state.

        Args:
            entity: The entity to evaluate the condition against.
            global_state: The global state of the simulation.

        Returns:
            bool: True if the condition is met, False otherwise.
        """
        pass

    def __and__(self, other):
        """
        Combine this condition with another using logical AND.

        Args:
            other (Condition): The other condition to combine with.

        Returns:
            CompositeCondition: A new composite condition representing the AND operation.
        """
        return CompositeCondition(operator.and_, [self, other])

    def __or__(self, other):
        """
        Combine this condition with another using logical OR.

        Args:
            other (Condition): The other condition to combine with.

        Returns:
            CompositeCondition: A new composite condition representing the OR operation.
        """
        return CompositeCondition(operator.or_, [self, other])

    def __invert__(self):
        """
        Invert this condition using logical NOT.

        Returns:
            CompositeCondition: A new composite condition representing the NOT operation.
        """
        return CompositeCondition(operator.not_, [self])

class AttributeCondition(Condition):
    """
    A condition that checks an attribute of an entity.

    This condition compares an attribute of an entity with an expected value
    using a specified comparison operator.
    """

    def __init__(self, attribute_name, expected_value, comparison=operator.eq):
        """
        Initialize the AttributeCondition.

        Args:
            attribute_name (str): The name of the attribute to check.
            expected_value: The expected value of the attribute.
            comparison (function, optional): The comparison function to use. Defaults to operator.eq.
        """
        self.attribute_name = attribute_name
        self.expected_value = expected_value
        self.comparison = comparison

    def evaluate(self, entity, global_state):
        """
        Evaluate the condition for a given entity and global state.

        Args:
            entity: The entity to evaluate the condition against.
            global_state: The global state of the simulation (unused in this condition).

        Returns:
            bool: True if the condition is met, False otherwise.
        """
        actual_value = entity.get_attribute(self.attribute_name)
        return self.comparison(actual_value, self.expected_value)

class GlobalCondition(Condition):
    """
    A condition that checks a value in the global state.

    This condition compares a value in the global state with an expected value
    using a specified comparison operator.
    """

    def __init__(self, global_key, expected_value, comparison=operator.eq):
        """
        Initialize the GlobalCondition.

        Args:
            global_key (str): The key to check in the global state.
            expected_value: The expected value of the global state key.
            comparison (function, optional): The comparison function to use. Defaults to operator.eq.
        """
        self.global_key = global_key
        self.expected_value = expected_value
        self.comparison = comparison

    def evaluate(self, entity, global_state):
        """
        Evaluate the condition for a given entity and global state.

        Args:
            entity: The entity to evaluate the condition against (unused in this condition).
            global_state: The global state of the simulation.

        Returns:
            bool: True if the condition is met, False otherwise.
        """
        actual_value = global_state.get(self.global_key)
        return self.comparison(actual_value, self.expected_value)

class CompositeCondition(Condition):
    """
    A condition that combines multiple conditions using a logical operator.

    This condition evaluates multiple conditions and combines their results
    using a specified logical operator.
    """

    def __init__(self, operator_func, conditions):
        """
        Initialize the CompositeCondition.

        Args:
            operator_func (function): The logical operator function to use (e.g., operator.and_, operator.or_).
            conditions (list): A list of Condition objects to combine.
        """
        self.operator_func = operator_func
        self.conditions = conditions

    def evaluate(self, entity, global_state):
        """
        Evaluate the composite condition for a given entity and global state.

        Args:
            entity: The entity to evaluate the conditions against.
            global_state: The global state of the simulation.

        Returns:
            bool: True if the composite condition is met, False otherwise.
        """
        results = [cond.evaluate(entity, global_state) for cond in self.conditions]
        return self.operator_func(*results)
