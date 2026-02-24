"""
pda_loader.py — instantiate a PushdownAutomataModel from gui/pda.json.

Usage
-----
from comp382_assignment_2.pda.pda_loader import load_cfl_pda, load_super_pda

cfl_model   = load_cfl_pda("an_bn")    # raw CFL PDA for individual CFL check
super_model = load_super_pda("an_bn")  # intersection SuperPDA for simulation
"""

import json
import os
from comp382_assignment_2.pda.pushdown_automata_model import PushdownAutomataModel
from comp382_assignment_2.super_pda.registry import get_super_pda, list_super_pda_keys

_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "gui", "pda.json"
)


def load_raw() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


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
    data = load_raw()
    cfls = {k: v for k, v in data["cfl_pdas"].items() if not k.startswith("_")}
    if name not in cfls:
        raise KeyError(f"Unknown CFL PDA '{name}'. Available: {list(cfls)}")
    return build_model(cfls[name])


def load_super_pda(name: str) -> PushdownAutomataModel:
    """Load an intersection SuperPDA model by key."""
    return build_model(load_super_pda_config(name))


def load_super_pda_config(name: str) -> dict:
    """Return the SuperPDA config dict from class implementation by key."""
    return get_super_pda(name).to_config()


# ── backward-compat shim ───────────────────────────────────────────────────────
def load_pda(name: str) -> PushdownAutomataModel:
    """Legacy alias: tries super_pdas first, then cfl_pdas."""
    data = load_raw()
    cfls   = {k: v for k, v in data["cfl_pdas"].items()   if not k.startswith("_")}
    try:
        return load_super_pda(name)
    except KeyError:
        pass
    if name in cfls:
        return build_model(cfls[name])
    raise KeyError(f"Unknown PDA '{name}'. CFL: {list(cfls)}")


def list_pdas() -> dict:
    """Return flat dict of all PDA configs (super_pdas + cfl_pdas) keyed by name."""
    data = load_raw()
    result = {k: get_super_pda(k).to_config() for k in list_super_pda_keys()}
    for k, v in data["cfl_pdas"].items():
        if not k.startswith("_"):
            result[k] = v
    return result

