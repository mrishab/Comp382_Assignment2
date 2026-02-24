from comp382_assignment_2.super_pda.base import BaseSuperPDA, Transition
from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.status import Status


class BnSuperPDA(BaseSuperPDA):
    key = "bn"
    description = "SuperPDA for R1(a*b*) ∩ C3(bⁿ) = bⁿ"
    source_dfa = "a_star_b_star"
    source_cfl = "bn"
    language = "{ bⁿ | n ≥ 1 }"
    example_strings = ["b", "bb", "bbb"]
    states = ["q0"]
    alphabet = ["b"]
    stack_alphabet = ["Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = ["q0"]
    transitions = [
        Transition("q0", "b", "Z", "q0", ["Z"]),
    ]

    def __init__(self):
        super().__init__()
        self.machine_status = Status.RUNNING
        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self.graph_edges()
        self.graph_nodes(self)

    def node_color(self, state: str, model=None) -> dict:
        active_state = model.current_state if model is not None else self.current_state
        if state == active_state:
            return {"background": Color.NODE_ACCEPTED_BG.value, "border": Color.NODE_ACCEPTED_BORDER.value}
        return {"background": Color.NODE_DEFAULT_BG.value, "border": Color.NODE_DEFAULT_BORDER.value}

    def graph_nodes(self, model=None) -> list[dict]:
        runtime = model or self
        positions = self.position_map()

        if not self.nodes:
            for state in self.states:
                x, y = positions[state]
                self.nodes.append(
                    {
                        "id": state,
                        "label": state,
                        "shape": "doublecircle" if state in self.final_states else "circle",
                        "size": 30,
                        "font": {"size": 15, "color": Color.TEXT_WHITE.value},
                        "x": x,
                        "y": y,
                        "fixed": {"x": True, "y": True},
                        "color": self.node_color(state, runtime),
                    }
                )
        else:
            for node in self.nodes:
                node["color"] = self.node_color(node["id"], runtime)

        return self.nodes

    def graph_edges(self) -> list[dict]:
        if not self.edges:
            self.edges = super().graph_edges()
        return self.edges

    def next_step(self, character: str):
        if self.machine_status in {Status.ACCEPTED, Status.REJECTED}:
            return {
                "transitioned": False,
                "consumed": False,
                "state": self.current_state,
                "stack": list(self.stack),
                "status": self.machine_status,
            }

        if character != "b":
            self.machine_status = Status.REJECTED
            return {
                "transitioned": False,
                "consumed": False,
                "state": self.current_state,
                "stack": list(self.stack),
                "status": self.machine_status,
            }

        self.current_state = "q0"
        self.consumed_input += character
        self.input_index += 1
        self.machine_status = Status.RUNNING

        if self.input_index == len(self.input_string):
            self.machine_status = Status.ACCEPTED

        self.graph_nodes(self)

        return {
            "transitioned": True,
            "consumed": True,
            "state": self.current_state,
            "stack": list(self.stack),
            "status": self.machine_status,
        }

    def is_accepted(self) -> bool:
        return self.machine_status == Status.ACCEPTED and bool(self.consumed_input)

    def is_stuck(self) -> bool:
        return self.machine_status == Status.REJECTED
