import json

from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.gui.html_view import VisHtmlView
from comp382_assignment_2.gui.pda_builder import PDABuilder

_BG = "#1a1a2a"
_STACK_NODE_ID = "__stack_head__"

_OPTIONS = {
    "nodes": {
        "font": {"size": 15, "color": "#ffffff"},
        "borderWidth": 3,
        "shadow": {"enabled": True},
    },
    "edges": {
        "font": {"size": 10, "color": "#dddddd", "strokeWidth": 0},
        "color": {"color": "#667799"},
        "smooth": {"type": "curvedCW", "roundness": 0.25},
        "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}},
    },
    "physics": {
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": {
            "gravitationalConstant": -80,
            "centralGravity": 0.01,
            "springLength": 140,
            "springConstant": 0.05,
        },
        "stabilization": {"iterations": 200, "fit": True},
    },
}


class SuperPDAView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.graph_view = VisHtmlView(bg_color=_BG)
        layout.addWidget(self.graph_view)

        self.render_placeholder()

    def render_placeholder(self):
        self._render_message("Select Regular + CFL to load Super PDA")

    def render_empty_language(self):
        self._render_message("∅ (empty language)")

    def render_graph(self, config: dict):
        builder = PDABuilder(config)
        stack_symbol = config.get("initial_stack_symbol", "Z")
        nodes = [
            {
                "id": _STACK_NODE_ID,
                "label": f"Stack\n{stack_symbol}",
                "color": {"background": "#2a3a55", "border": "#4A90D9"},
                "shape": "box",
                "size": 30,
                "font": {"size": 13, "color": "#cfe5ff"},
                "x": 0,
                "y": -450,
                "fixed": {"x": True, "y": True},
            },
            *builder.build_nodes(),
        ]
        edges = [
            {
                "from": edge["source"],
                "to": edge["to"],
                "label": edge.get("label", ""),
            }
            for edge in builder.build_edges()
        ]
        self.graph_view.set_graph(nodes, edges, _OPTIONS)

    def _render_message(self, message: str):
        nodes = [{
            "id": "hint",
            "label": message,
            "color": {"background": "#1e2a3e", "border": "#334466"},
            "shape": "box",
            "size": 35,
            "font": {"size": 14, "color": "#556688"},
        }]
        edges = []
        options = json.loads(json.dumps(_OPTIONS))
        options["physics"]["enabled"] = False
        self.graph_view.set_graph(nodes, edges, options)
