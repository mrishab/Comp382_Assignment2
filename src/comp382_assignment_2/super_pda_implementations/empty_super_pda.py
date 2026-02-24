from comp382_assignment_2.super_pda.base import BaseSuperPDA
from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.status import Status


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

    def __init__(self):
        super().__init__()
        self.machine_status = Status.RUNNING
        self.nodes: list[dict] = []
        self.edges: list[dict] = []
        self.graph_edges()
        self.graph_nodes(self)

    def load_input(self, input_string: str) -> None:
        super().load_input(input_string)
        self.machine_status = Status.ACCEPTED if input_string == "" else Status.REJECTED
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
                        "shape": "circle",
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
            self.edges = []
        return self.edges

    def next_step(self, character: str):
        self.machine_status = Status.REJECTED
        return {
            "transitioned": False,
            "consumed": False,
            "state": self.current_state,
            "stack": list(self.stack),
            "status": self.machine_status,
        }

    def is_accepted(self) -> bool:
        return self.machine_status == Status.ACCEPTED

    def is_stuck(self) -> bool:
        return self.machine_status == Status.REJECTED
