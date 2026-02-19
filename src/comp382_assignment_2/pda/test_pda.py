"""
test_pda.py — Verify all PDA configs load and accept their example strings.
"""

import pytest
from comp382_assignment_2.pda.pda_loader import load_pda, list_pdas


def _run_pda(name: str, input_str: str) -> bool:
    """Load a PDA by config key, run it on input_str, return acceptance."""
    model = load_pda(name)
    model.load_input(input_str)
    while not model.is_stuck() and not model.is_accepted():
        model.step()
    return model.is_accepted()


# ── Parameterised: every PDA must accept its own example_strings ─────────

_PDAS = list_pdas()

_ACCEPT_CASES = [
    (name, s) for name, cfg in _PDAS.items() for s in cfg.get("example_strings", [])
]


@pytest.mark.parametrize(
    "name,input_str", _ACCEPT_CASES, ids=[f"{n}:{s}" for n, s in _ACCEPT_CASES]
)
def test_accept_example_strings(name: str, input_str: str):
    assert _run_pda(name, input_str), f"PDA '{name}' should accept '{input_str}'"


# ── Reject cases ─────────────────────────────────────────────────────────

_REJECT_CASES = [
    ("an_bn", "aab"),  # unbalanced
    ("an_bn", "a"),  # missing b's
    ("an_bn", ""),  # empty (n>=1)
    ("a_bn", "b"),  # must start with 'a'
    ("a_bn", "ba"),  # wrong order
    ("an", "ab"),  # no b's allowed
    ("an", "b"),  # only a's
    ("a_bn_a", "a"),  # needs trailing 'a'
    ("a_bn_a", "abb"),  # missing trailing 'a'
    ("aa", "a"),  # only "aa" accepted
    ("aa", "aaa"),  # too many
    ("bn", "a"),  # only b's
    ("bn", ""),  # n>=1
    ("empty", "a"),  # nothing accepted
    ("empty", "b"),
    ("empty", ""),
]


@pytest.mark.parametrize(
    "name,input_str", _REJECT_CASES, ids=[f"{n}:reject:{s!r}" for n, s in _REJECT_CASES]
)
def test_reject_strings(name: str, input_str: str):
    assert not _run_pda(name, input_str), f"PDA '{name}' should reject '{input_str}'"


# ── Intersection correctness ────────────────────────────────────────────


def test_intersection_a_star_b_star_x_an_bn():
    """a*b* ∩ aⁿbⁿ = aⁿbⁿ"""
    assert _run_pda("an_bn", "aabb")
    assert not _run_pda("an_bn", "aab")


def test_intersection_a_star_x_bn_is_empty():
    """a* ∩ bⁿ = ∅"""
    # The 'empty' PDA has no final states — rejects everything
    for s in ["", "a", "b", "ab", "aa", "bb"]:
        assert not _run_pda("empty", s)
