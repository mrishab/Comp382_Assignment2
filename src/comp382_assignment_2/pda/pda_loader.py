"""
pda_loader.py — instantiate PushdownAutomataModel from SuperPDA class implementations.

Usage
-----
from comp382_assignment_2.pda.pda_loader import load_cfl_pda, load_super_pda

cfl_model   = load_cfl_pda("an_bn")    # raw CFL PDA for individual CFL check
super_model = load_super_pda("an_bn")  # intersection SuperPDA for simulation
"""

from comp382_assignment_2.pda.pushdown_automata_model import PushdownAutomataModel
from comp382_assignment_2.super_pda.registry import get_super_pda, list_super_pda_keys


def parse_transitions(transition_list: list) -> dict:
    """
    Convert the JSON transition array into the dict format expected by
    PushdownAutomataModel:
        { (state, input|None, stack_top): [(next_state, push_list)] }
    """
    table: dict = {}
    for t in transition_list:
        key = (t["from"], t["input"], t["stack_top"])
        table.setdefault(key, []).append((t["to"], t["push"]))
    return table


def build_model(cfg: dict) -> PushdownAutomataModel:
    return PushdownAutomataModel(
        states=set(cfg["states"]),
        alphabet=set(cfg["alphabet"]),
        stack_alphabet=set(cfg["stack_alphabet"]),
        transitions=parse_transitions(cfg["transitions"]),
        initial_state=cfg["initial_state"],
        initial_stack_symbol=cfg["initial_stack_symbol"],
        final_states=set(cfg["final_states"]),
    )


def load_cfl_pda(name: str) -> PushdownAutomataModel:
    """Load a raw CFL PDA by key (an_bn | a_bn_a | bn)."""
    cfl_keys = {"an_bn", "a_bn_a", "bn"}
    if name not in cfl_keys:
        raise KeyError(f"Unknown CFL PDA '{name}'. Available: {sorted(cfl_keys)}")
    return load_super_pda(name)


def load_super_pda(name: str) -> PushdownAutomataModel:
    """Load an intersection SuperPDA model by key."""
    return build_model(load_super_pda_config(name))


def load_super_pda_config(name: str) -> dict:
    """Return the SuperPDA config dict from class implementation by key."""
    return get_super_pda(name).to_config()


# ── backward-compat shim ───────────────────────────────────────────────────────
def load_pda(name: str) -> PushdownAutomataModel:
    """Legacy alias for load_super_pda."""
    return load_super_pda(name)


def list_pdas() -> dict:
    """Return flat dict of all PDA configs keyed by name."""
    return {k: get_super_pda(k).to_config() for k in list_super_pda_keys()}

