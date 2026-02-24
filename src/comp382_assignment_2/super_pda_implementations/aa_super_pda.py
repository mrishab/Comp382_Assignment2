from comp382_assignment_2.super_pda.base import BaseSuperPDA, Transition


class AASuperPDA(BaseSuperPDA):
    key = "aa"
    description = "SuperPDA for R1(a*b*) ∩ C2(abⁿa) = {aa} and R3(a*) ∩ C2(abⁿa) = {aa}"
    source_dfa = "a_star_b_star | a_star"
    source_cfl = "a_bn_a"
    language = "{ aa }"
    example_strings = ["aa"]
    states = ["q0", "q1", "q2", "q3"]
    alphabet = ["a"]
    stack_alphabet = ["Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = ["q3"]
    transitions = [
        Transition("q0", "a", "Z", "q1", ["Z"]),
        Transition("q1", "a", "Z", "q2", ["Z"]),
        Transition("q2", None, "Z", "q3", ["Z"]),
    ]

    def next_step(self, character: str):
        return super().next_step(character)
