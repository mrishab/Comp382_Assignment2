"""
Example PDA: recognises the CFL  a^n b^n  (n ≥ 1)

States   : q0, q1, q2
Alphabet : {a, b}
Stack Σ  : {A, Z}  (Z = bottom-of-stack marker)

Transitions
-----------
(q0, a, Z)  → (q0, [A, Z])   # first a: push A over Z
(q0, a, A)  → (q0, [A, A])   # subsequent a's: push A
(q0, b, A)  → (q1, [])       # first b: pop one A, move to q1
(q1, b, A)  → (q1, [])       # subsequent b's: pop A
(q1, ε, Z)  → (q2, [Z])      # all b's matched: accept
"""

from comp382_assignment_2.pda.pushdown_automata_model import PushdownAutomataModel


def create_an_bn_pda() -> PushdownAutomataModel:
    return PushdownAutomataModel(
        states={"q0", "q1", "q2"},
        alphabet={"a", "b"},
        stack_alphabet={"A", "Z"},
        transitions={
            ("q0", "a", "Z"): [("q0", ["A", "Z"])],
            ("q0", "a", "A"): [("q0", ["A", "A"])],
            ("q0", "b", "A"): [("q1", [])],
            ("q1", "b", "A"): [("q1", [])],
            ("q1", None, "Z"): [("q2", ["Z"])],
        },
        initial_state="q0",
        initial_stack_symbol="Z",
        final_states={"q2"},
    )
