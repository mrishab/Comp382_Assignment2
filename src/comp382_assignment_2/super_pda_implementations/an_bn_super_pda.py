from comp382_assignment_2.super_pda.base import BaseSuperPDA, Transition


class AnBnSuperPDA(BaseSuperPDA):
    key = "an_bn"
    description = "SuperPDA for R1(a*b*) ∩ C1(aⁿbⁿ) = aⁿbⁿ"
    source_dfa = "a_star_b_star"
    source_cfl = "an_bn"
    language = "{ aⁿbⁿ | n ≥ 1 }"
    example_strings = ["ab", "aabb", "aaabbb"]
    states = ["q0", "q1", "q2"]
    alphabet = ["a", "b"]
    stack_alphabet = ["A", "Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = ["q2"]
    transitions = [
        Transition("q0", "a", "Z", "q0", ["A", "Z"]),
        Transition("q0", "a", "A", "q0", ["A", "A"]),
        Transition("q0", "b", "A", "q1", []),
        Transition("q1", "b", "A", "q1", []),
        Transition("q1", None, "Z", "q2", ["Z"]),
    ]

    def next_step(self, character: str):
        return super().next_step(character)
