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
