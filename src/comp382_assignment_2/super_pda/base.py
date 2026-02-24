from __future__ import annotations

from dataclasses import dataclass

_EPS = "ε"
_ARR = "→"

NODE_COLOURS = {
    "default": {"background": "#4A90D9", "border": "#2C5F8A"},
    "active": {"background": "#FFD700", "border": "#B8860B"},
    "accept": {"background": "#5CB85C", "border": "#3A7A3A"},
    "initial": {"background": "#9B59B6", "border": "#6C3483"},
    "stuck": {"background": "#E74C3C", "border": "#922B21"},
}


@dataclass(frozen=True)
class Transition:
    source: str
    input_symbol: str | None
    stack_top: str | None
    target: str
    push: list[str]


class BaseSuperPDA:
    key: str = ""
    description: str = ""
    source_dfa: str = ""
    source_cfl: str = ""
    language: str = ""
    example_strings: list[str] = []
    states: list[str] = []
    alphabet: list[str] = []
    stack_alphabet: list[str] = []
    initial_state: str = ""
    initial_stack_symbol: str = "Z"
    final_states: list[str] = []
    transitions: list[Transition] = []

    def position_map(self) -> dict[str, tuple[int, int]]:
        spacing = 180
        start_x = -((len(self.states) - 1) * spacing) // 2
        return {state: (start_x + idx * spacing, 0) for idx, state in enumerate(self.states)}

    def to_config(self) -> dict:
        return {
            "description": self.description,
            "source_dfa": self.source_dfa,
            "source_cfl": self.source_cfl,
            "language": self.language,
            "example_strings": list(self.example_strings),
            "states": list(self.states),
            "alphabet": list(self.alphabet),
            "stack_alphabet": list(self.stack_alphabet),
            "initial_state": self.initial_state,
            "initial_stack_symbol": self.initial_stack_symbol,
            "final_states": list(self.final_states),
            "transitions": [
                {
                    "from": t.source,
                    "input": t.input_symbol,
                    "stack_top": t.stack_top,
                    "to": t.target,
                    "push": list(t.push),
                }
                for t in self.transitions
            ],
        }

    def node_color(self, state: str, model=None) -> dict:
        if model is not None:
            if state == model.current_state:
                if model.is_stuck():
                    return NODE_COLOURS["stuck"]
                if model.is_accepted():
                    return NODE_COLOURS["accept"]
                return NODE_COLOURS["active"]
            if state in model.final_states:
                return NODE_COLOURS["accept"]
            if state == model.initial_state:
                return NODE_COLOURS["initial"]
            return NODE_COLOURS["default"]

        if state in self.final_states:
            return NODE_COLOURS["accept"]
        if state == self.initial_state:
            return NODE_COLOURS["initial"]
        return NODE_COLOURS["default"]

    def graph_nodes(self, model=None) -> list[dict]:
        positions = self.position_map()
        nodes: list[dict] = []
        for state in self.states:
            x, y = positions[state]
            nodes.append(
                {
                    "id": state,
                    "label": state,
                    "color": self.node_color(state, model),
                    "shape": "doublecircle" if state in self.final_states else "circle",
                    "size": 30,
                    "font": {"size": 15, "color": "#ffffff"},
                    "x": x,
                    "y": y,
                    "fixed": {"x": True, "y": True},
                }
            )
        return nodes

    def graph_edges(self) -> list[dict]:
        merged: dict[tuple[str, str], list[str]] = {}
        for t in self.transitions:
            input_symbol = t.input_symbol if t.input_symbol is not None else _EPS
            stack_top = t.stack_top if t.stack_top is not None else _EPS
            push = "|".join(t.push) if t.push else _EPS
            label = f"{input_symbol},{stack_top} {_ARR} {push}"
            merged.setdefault((t.source, t.target), []).append(label)

        return [
            {"from": src, "to": dst, "label": " | ".join(labels)}
            for (src, dst), labels in merged.items()
        ]
