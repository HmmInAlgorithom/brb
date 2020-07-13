from typing import List, Dict, Any

import numpy as np


class AttributeInput():
    """An input to the BRB system.

    Consists of a set of antecedent attribute values and degrees of belief.

    Attributes:
        attr_input: A^*. Relates antecedent attributes with values and belief degrees.
    """

    def __init__(self, attr_input: Dict[str, Tuple[Any, float]]):
        self.attr_input = attr_input

    # TODO: add transformation methods

class Rule():
    """A rule definition in a BRB system.

    It translates expert knowledge into a mapping between the antecedents and the consequents. We assume that it is defined as a pure AND rules, that is, the only logical relation between the input attributes is the AND function.

    Attributes:
        model: The rule-base model to which this rule should apply to.
        A_values: A^k. Dictionary that matches reference values for each antecedent attribute that activates the rule.
        delta: \delta_k. Relative weights of antecedent attributes.
        theta: \theta_k. Rule weight.
        beta: \bar{\beta}. Expected belief degrees of consequents if rule is (completely) activated.
    """

    def __init__(self, A_values: Dict[str, Any], delta: Dict[str, float], theta: float, beta: Dict[Any, Any]):
        self.A_values = A_values

        # there must exist a weight for all antecedent attributes that activate the rule
        for U_i in A_values.keys():
            assert U_i in delta.keys()
        self.delta = delta

        self.theta = theta
        self.beta = beta

    def get_matching_degree(self, X: AttributeInput) -> float:
        """Calculates the matching degree of the rule based on input `X`.
        """
        self._assert_input(X)

        norm_delta = {attr: d / max(self.delta.values()) for attr, d in self.delta.items()}
        weighted_alpha = [X.attr_input[attr] ^ norm_delta[attr] for attr in self.A_values.keys()]

        return np.prod(weighted_alpha)

    def _assert_input(self, X: AttributeInput):
        """Checks if `X` is proper.

        Guarantees that all the necessary attributes are present in X.
        """
        rule_attributes = set(self.A_values.keys())
        input_attributes = set(X.attr_input.keys())
        assert rule_attributes.intersection(input_attributes) == rule_attributes


class RuleBaseModel():
    """Parameters for the model.
    
    It contains the basic, standard information that will be used to manage the information and apply the operations.

    Attributes:
        U: Antecendent attributes' names.
        A: Referential values for each antecedent.
        D: Consequent referential values.
        F: ?
        rules: List of rules.
    """
    def __init__(self, U: List[str], A: Dict[str, List[Any]], D: List[Any], F):
        self.U = U
        self.A = A
        self.D = D
        self.F = F

        self.rules = list()

    def add_rule(self, new_rule: Rule):
        """Adds a new rule to the model.

        Verifies if the given rule agrees with the model settings and adds it to `.rules`.
        """
        # all reference values must be related to an attribute
        assert new_rule.A_values.keys() in self.U

        # the reference values that activate the rule must be a valid referential value in the self
        for U_i, A_i in new_rule.A_values.items():
            assert A_i in self.A[U_i]

        # the belief degrees must be applied to values defined by the self
        for D_n in new_rule.beta.keys():
            assert D_n in self.D

        self.rules.append(new_rule)

    def run(self, X: AttributeInput):
        """Infer the output based on the RIMER approach.

        Args:
            X: Attribute's data to be fed to the rules.
        """
        # input for all valid antecedents must be provided
        for U_i in X.attr_input.keys():
            assert U_i in self.U

        # matching degree
        alpha = [rule.get_matching_degree(X) for rule in self.rules]
