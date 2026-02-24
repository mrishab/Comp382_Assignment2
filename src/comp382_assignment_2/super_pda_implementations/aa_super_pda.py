from comp382_assignment_2.super_pda.base import BaseSuperPDA, Transition
from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.status import Status


class AASuperPDA(BaseSuperPDA):
    key = "aa"
    description = "SuperPDA for R1(a*b*) ∩ C2(abⁿa) = {aa} and R3(a*) ∩ C2(abⁿa) = {aa}"
    source_dfa = "a_star_b_star | a_star"
    source_cfl = "a_bn_a"
    language = "{ aa }"
    example_strings = ["aa"]
    states = ["q0", "q1", "q2"]
    alphabet = ["a"]
    stack_alphabet = ["Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = ["q2"]
    transitions = [
        Transition("q0", "a", "Z", "q1", ["Z"]),
        Transition("q1", "a", "Z", "q2", ["Z"]),
    ]

    def __init__(self):
        super().__init__()
        self.machine_status = Status.RUNNING.value
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
        if self.machine_status in {Status.ACCEPTED.value, Status.REJECTED.value}:
            return {
                "transitioned": False,
                "consumed": False,
                "state": self.current_state,
                "stack": list(self.stack),
                "status": self.machine_status,
            }

        if character != "a":
            self.machine_status = Status.REJECTED.value
            return {
                "transitioned": False,
                "consumed": False,
                "state": self.current_state,
                "stack": list(self.stack),
                "status": self.machine_status,
            }

        transitioned = False

        if self.current_state == "q0":
            self.current_state = "q1"
            transitioned = True
        elif self.current_state == "q1":
            self.current_state = "q2"
            transitioned = True
            self.machine_status = Status.ACCEPTED.value
        else:
            self.machine_status = Status.REJECTED.value

        if transitioned:
            self.consumed_input += character
            self.input_index += 1
            if self.current_state != "q2":
                self.machine_status = Status.RUNNING.value

        self.graph_nodes(self)

        return {
            "transitioned": transitioned,
            "consumed": transitioned,
            "state": self.current_state,
            "stack": list(self.stack),
            "status": self.machine_status,
        }
