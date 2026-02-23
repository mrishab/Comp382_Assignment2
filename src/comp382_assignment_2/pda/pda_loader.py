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

_CONFIG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "gui", "pda.json"
)


def _load_raw() -> dict:
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _parse_transitions(transition_list: list) -> dict:
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


def _build_model(cfg: dict) -> PushdownAutomataModel:
    return PushdownAutomataModel(
        states=set(cfg["states"]),
        alphabet=set(cfg["alphabet"]),
        stack_alphabet=set(cfg["stack_alphabet"]),
        transitions=_parse_transitions(cfg["transitions"]),
        initial_state=cfg["initial_state"],
        initial_stack_symbol=cfg["initial_stack_symbol"],
        final_states=set(cfg["final_states"]),
    )


def load_cfl_pda(name: str) -> PushdownAutomataModel:
    """Load a raw CFL PDA by key (an_bn | a_bn_a | bn)."""
    data = _load_raw()
    cfls = {k: v for k, v in data["cfl_pdas"].items() if not k.startswith("_")}
    if name not in cfls:
        raise KeyError(f"Unknown CFL PDA '{name}'. Available: {list(cfls)}")
    return _build_model(cfls[name])


def load_super_pda(name: str) -> PushdownAutomataModel:
    """Load an intersection SuperPDA model by key."""
    return _build_model(load_super_pda_config(name))


def load_super_pda_config(name: str) -> dict:
    """Return the raw config dict for a SuperPDA by key (an_bn | aa | a_bn_a | bn | empty)."""
    data = _load_raw()
    supers = {k: v for k, v in data["super_pdas"].items() if not k.startswith("_")}
    if name not in supers:
        raise KeyError(f"Unknown SuperPDA '{name}'. Available: {list(supers)}")
    return supers[name]


# ── backward-compat shim ───────────────────────────────────────────────────────
def load_pda(name: str) -> PushdownAutomataModel:
    """Legacy alias: tries super_pdas first, then cfl_pdas."""
    data = _load_raw()
    supers = {k: v for k, v in data["super_pdas"].items() if not k.startswith("_")}
    cfls   = {k: v for k, v in data["cfl_pdas"].items()   if not k.startswith("_")}
    if name in supers:
        return _build_model(supers[name])
    if name in cfls:
        return _build_model(cfls[name])
    raise KeyError(f"Unknown PDA '{name}'. Super: {list(supers)}  CFL: {list(cfls)}")


def list_pdas() -> dict:
    """Return flat dict of all PDA configs (super_pdas + cfl_pdas) keyed by name."""
    data = _load_raw()
    result = {}
    for section in ("super_pdas", "cfl_pdas"):
        for k, v in data[section].items():
            if not k.startswith("_"):
                result[k] = v
    return result

