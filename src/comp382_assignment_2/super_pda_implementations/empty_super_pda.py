from comp382_assignment_2.super_pda.base import BaseSuperPDA


class EmptySuperPDA(BaseSuperPDA):
    key = "empty"
    description = "SuperPDA sentinel for ∅"
    source_dfa = "a_b_star_a | a_star"
    source_cfl = "an_bn | bn"
    language = "∅"
    example_strings = []
    states = ["q0"]
    alphabet = []
    stack_alphabet = ["Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = []
    transitions = []

    def next_step(self, character: str):
        return super().next_step(character)
