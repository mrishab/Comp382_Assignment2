"""
pda_loader.py — instantiate a PushdownAutomataModel directly from pda_configs.json.

Usage
-----
from comp382_assignment_2.pda.pda_loader import load_pda, list_pdas

model = load_pda("an_bn")            # load by key
for key, cfg in list_pdas().items(): # iterate all
    print(key, cfg["description"])
"""

import json
import os
from comp382_assignment_2.pda.pushdown_automata_model import PushdownAutomataModel

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "pda_configs.json")


def _parse_transitions(transition_list: list) -> dict:
    """
    Convert the JSON array of transition objects into the dict format
    expected by PushdownAutomataModel:
        {(state, input|None, stack_top): [(next_state, push_list)]}
    """
    table: dict = {}
    for t in transition_list:
        key = (t["from"], t["input"], t["stack_top"])
        entry = (t["to"], t["push"])
        table.setdefault(key, []).append(entry)
    return table


def list_pdas() -> dict:
    """Return the raw JSON config dict (all keys)."""
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in data.items() if not k.startswith("_")}


def load_pda(name: str) -> PushdownAutomataModel:
    """
    Instantiate a PushdownAutomataModel by its config key.
    Valid keys: an_bn, a_bn, an, a_bn_a, aa, bn, empty
    """
    configs = list_pdas()
    if name not in configs:
        raise KeyError(f"Unknown PDA '{name}'. Available: {list(configs)}")

    cfg = configs[name]
    return PushdownAutomataModel(
        states=set(cfg["states"]),
        alphabet=set(cfg["alphabet"]),
        stack_alphabet=set(cfg["stack_alphabet"]),
        transitions=_parse_transitions(cfg["transitions"]),
        initial_state=cfg["initial_state"],
        initial_stack_symbol=cfg["initial_stack_symbol"],
        final_states=set(cfg["final_states"]),
    )
