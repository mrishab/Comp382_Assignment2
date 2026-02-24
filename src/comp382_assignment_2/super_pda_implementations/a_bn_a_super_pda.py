from comp382_assignment_2.super_pda.base import BaseSuperPDA, Transition


class AABNASuperPDA(BaseSuperPDA):
    key = "a_bn_a"
    description = "SuperPDA for R2(ab*a) ∩ C2(abⁿa) = abⁿa"
    source_dfa = "a_b_star_a"
    source_cfl = "a_bn_a"
    language = "{ abⁿa | n ≥ 0 }"
    example_strings = ["aa", "aba", "abba", "abbba"]
    states = ["q0", "q1", "q2", "q3"]
    alphabet = ["a", "b"]
    stack_alphabet = ["Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = ["q3"]
    transitions = [
        Transition("q0", "a", "Z", "q1", ["Z"]),
        Transition("q1", "b", "Z", "q1", ["Z"]),
        Transition("q1", "a", "Z", "q2", ["Z"]),
        Transition("q2", None, "Z", "q3", ["Z"]),
    ]

    def next_step(self, character: str):
        return super().next_step(character)
