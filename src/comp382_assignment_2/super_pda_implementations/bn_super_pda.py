from comp382_assignment_2.super_pda.base import BaseSuperPDA, Transition


class BnSuperPDA(BaseSuperPDA):
    key = "bn"
    description = "SuperPDA for R1(a*b*) ∩ C3(bⁿ) = bⁿ"
    source_dfa = "a_star_b_star"
    source_cfl = "bn"
    language = "{ bⁿ | n ≥ 1 }"
    example_strings = ["b", "bb", "bbb"]
    states = ["q0", "q1", "q2"]
    alphabet = ["b"]
    stack_alphabet = ["Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = ["q2"]
    transitions = [
        Transition("q0", "b", "Z", "q1", ["Z"]),
        Transition("q1", "b", "Z", "q1", ["Z"]),
        Transition("q1", None, "Z", "q2", ["Z"]),
    ]

    def next_step(self, character: str):
        return super().next_step(character)
