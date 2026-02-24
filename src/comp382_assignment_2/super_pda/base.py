from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from comp382_assignment_2.common.colors import Color

_EPS = "ε"
_ARR = "→"

NODE_COLOURS = {
    "default": {"background": Color.NODE_DEFAULT_BG.value, "border": Color.NODE_DEFAULT_BORDER.value},
    "active": {"background": Color.NODE_ACTIVE_BG.value, "border": Color.NODE_ACTIVE_BORDER.value},
    "accepted": {"background": Color.NODE_ACCEPTED_BG.value, "border": Color.NODE_ACCEPTED_BORDER.value},
    "initial": {"background": Color.NODE_INITIAL_BG.value, "border": Color.NODE_INITIAL_BORDER.value},
    "rejected": {"background": Color.NODE_REJECTED_BG.value, "border": Color.NODE_REJECTED_BORDER.value},
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

    def __init__(self):
        self.reset_runtime()

    def reset_runtime(self) -> None:
        self.current_state = self.initial_state
        self.stack: list[str] = [self.initial_stack_symbol]
        self.input_string = ""
        self.input_index = 0
        self.consumed_input = ""

    def load_input(self, input_string: str) -> None:
        self.reset_runtime()
        self.input_string = input_string

    def _match_transition(self, input_symbol: str | None) -> Transition | None:
        stack_top = self.stack[-1] if self.stack else None

        for transition in self.transitions:
            if transition.source != self.current_state:
                continue
            if transition.input_symbol != input_symbol:
                continue
            if transition.stack_top is not None and transition.stack_top != stack_top:
                continue
            return transition

        for transition in self.transitions:
            if transition.source != self.current_state:
                continue
            if transition.input_symbol is not None:
                continue
            if transition.stack_top is not None and transition.stack_top != stack_top:
                continue
            return transition

        return None

    def _apply_transition(self, transition: Transition) -> None:
        if transition.stack_top is not None and self.stack:
            self.stack.pop()

        for symbol in reversed(transition.push):
            self.stack.append(symbol)

        self.current_state = transition.target

    def next_step(self, character: str) -> dict[str, Any]:
        transition = self._match_transition(character)
        if transition is None:
            return {
                "transitioned": False,
                "consumed": False,
                "state": self.current_state,
                "stack": list(self.stack),
            }

        self._apply_transition(transition)

        consumed = transition.input_symbol is not None
        if consumed:
            self.consumed_input += character
            self.input_index += 1

        return {
            "transitioned": True,
            "consumed": consumed,
            "state": self.current_state,
            "stack": list(self.stack),
        }

    def is_accepted(self) -> bool:
        return self.current_state in self.final_states and self.input_index == len(self.input_string)

    def is_stuck(self) -> bool:
        current_char = self.input_string[self.input_index] if self.input_index < len(self.input_string) else None
        return self._match_transition(current_char) is None

    def is_stuck_for(self, character: str) -> bool:
        return self._match_transition(character) is None

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
                    return NODE_COLOURS["rejected"]
                if model.is_accepted():
                    return NODE_COLOURS["accepted"]
                return NODE_COLOURS["active"]
            if state in model.final_states:
                return NODE_COLOURS["accepted"]
            if state == model.initial_state:
                return NODE_COLOURS["initial"]
            return NODE_COLOURS["default"]

        if state in self.final_states:
            return NODE_COLOURS["accepted"]
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
                    "font": {"size": 15, "color": Color.TEXT_WHITE.value},
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
