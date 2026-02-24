from pyvis.network import Network
from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.flow_diagram_status import FlowDiagramStatus
from comp382_assignment_2.gui.html_view import VisHtmlView
from comp382_assignment_2.gui.node_style_map import NodeStyleMap

_BG = Color.GRAPH_BACKGROUND_DARK.value

_LEVELS = {
    "Regex": 0,
    "CFL": 0,
    "DFA": 1,
    "PDA": 1,
    "∩ Gate": 2,
    "Input": 3,
    "Language": 3,
    "Result": 4,
}

_EDGES = [
    ("Regex", "DFA"),
    ("CFL", "PDA"),
    ("DFA", "∩ Gate"),
    ("PDA", "∩ Gate"),
    ("∩ Gate", "Language"),
    ("Input", "Language"),
    ("Language", "Result"),
]


class FlowDiagram(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = VisHtmlView(bg_color=_BG)
        layout.addWidget(self.view)

        self.result_text: str = ""
        self.language_label: str = ""
        self.selected_regex: str = ""
        self.selected_cfl: str = ""
        self.input_value: str = ""

        self.render()

    def render(self):
        regex_label = self.selected_regex or "Regex"
        cfl_label = self.selected_cfl or "CFL"
        dfa_label = "DFA"
        pda_label = "PDA"
        gate_label = "∩ Gate"
        input_label = self.input_value or "Input"
        language_label = self.language_label or "Language"
        result_label = self.result_text or "Result"

        node_defs = {
            "Regex": (regex_label, NodeStyleMap.flow(FlowDiagramStatus.START), "ellipse", 28),
            "CFL": (cfl_label, NodeStyleMap.flow(FlowDiagramStatus.START), "ellipse", 28),
            "DFA": (dfa_label, NodeStyleMap.flow(FlowDiagramStatus.IDLE), "ellipse", 32),
            "PDA": (pda_label, NodeStyleMap.flow(FlowDiagramStatus.IDLE), "ellipse", 32),
            "∩ Gate": (gate_label, NodeStyleMap.flow(FlowDiagramStatus.GATE), "box", 30),
            "Input": (input_label, NodeStyleMap.flow(FlowDiagramStatus.INPUT), "box", 28),
            "Language": (language_label, NodeStyleMap.flow(FlowDiagramStatus.LANG), "box", 28),
            "Result": (result_label, NodeStyleMap.flow(FlowDiagramStatus.RESULT), "box", 30),
        }

        net = Network(height="100%", width="100%", directed=True, notebook=False, bgcolor=_BG)
        VisHtmlView.apply_flow_diagram_options(net)

        for node_id, (label, color, shape, size) in node_defs.items():
            net.add_node(
                node_id,
                label=label,
                color=color,
                shape=shape,
                size=size,
                level=_LEVELS[node_id],
            )

        for source, target in _EDGES:
            net.add_edge(source, target, label="")

        self.view.set_graph_from_net(net)
