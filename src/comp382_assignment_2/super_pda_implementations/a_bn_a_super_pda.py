from comp382_assignment_2.super_pda.base import BaseSuperPDA, Transition
from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.status import Status


class AABNASuperPDA(BaseSuperPDA):
    key = "a_bn_a"
    description = "SuperPDA for R2(ab*a) ∩ C2(abⁿa) = abⁿa"
    source_dfa = "a_b_star_a"
    source_cfl = "a_bn_a"
    language = "{ abⁿa | n ≥ 0 }"
    example_strings = ["aa", "aba", "abba", "abbba"]
    states = ["q0", "q1", "q2", "q3"]
    alphabet = ["a", "b"]
    stack_alphabet = ["Z"]
    initial_state = "q0"
    initial_stack_symbol = "Z"
    final_states = ["q3"]
    transitions = [
        Transition("q0", "a", "Z", "q1", ["Z"]),
        Transition("q1", "b", "Z", "q2", ["Z"]),
        Transition("q1", "a", "Z", "q3", ["Z"]),
        Transition("q2", "b", "Z", "q2", ["Z"]),
        Transition("q2", "a", "Z", "q3", ["Z"]),
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

        if character not in {"a", "b"}:
            self.machine_status = Status.REJECTED
            return {
                "transitioned": False,
                "consumed": False,
                "state": self.current_state,
                "stack": list(self.stack),
                "status": self.machine_status,
            }

        transitioned = False

        if self.current_state == "q0":
            if character == "a":
                self.current_state = "q1"
                transitioned = True
            else:
                self.machine_status = Status.REJECTED
        elif self.current_state == "q1":
            if character == "b":
                self.current_state = "q2"
                transitioned = True
            elif character == "a":
                self.current_state = "q3"
                transitioned = True
                self.machine_status = Status.ACCEPTED
            else:
                self.machine_status = Status.REJECTED
        elif self.current_state == "q2":
            if character == "b":
                self.current_state = "q2"
                transitioned = True
            elif character == "a":
                self.current_state = "q3"
                transitioned = True
                self.machine_status = Status.ACCEPTED
            else:
                self.machine_status = Status.REJECTED
        else:
            self.machine_status = Status.REJECTED

        if transitioned:
            self.consumed_input += character
            self.input_index += 1
            if self.current_state != "q3":
                self.machine_status = Status.RUNNING

        self.graph_nodes(self)

        return {
            "transitioned": transitioned,
            "consumed": transitioned,
            "state": self.current_state,
            "stack": list(self.stack),
            "status": self.machine_status,
        }
