import json

from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.gui.html_view import VisHtmlView
from comp382_assignment_2.super_pda.base import BaseSuperPDA

_BG = Color.GRAPH_BACKGROUND_DARK.value
_STACK_NODE_ID = "__stack_head__"

_OPTIONS = {
    "nodes": {
        "font": {"size": 15, "color": Color.TEXT_WHITE.value},
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
        "enabled": False,
    },
}


class SuperPDAView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.graph_view = VisHtmlView(bg_color=_BG)
        layout.addWidget(self.graph_view)

        self._super_pda: BaseSuperPDA | None = None
        self._base_edges: list[dict] = []
        self._stack_symbol: str = "Z"

        self.render_placeholder()

    def render_placeholder(self):
        self.render_message("Select Regular + CFL to load Super PDA")

    def render_empty_language(self):
        self.render_message("∅ (empty language)")

    def render_graph(self, super_pda: BaseSuperPDA):
        self._super_pda = super_pda
        self._stack_symbol = super_pda.initial_stack_symbol
        self._base_edges = super_pda.graph_edges()
        self.render_nodes(super_pda.graph_nodes())

    def update_state(self, model):
        if self._super_pda is None:
            return
        nodes = self._super_pda.graph_nodes(model=model)
        stack_head = model.stack[-1] if model.stack else self._stack_symbol
        self.render_nodes(nodes, stack_head=stack_head)

    def reset_state(self):
        if self._super_pda is None:
            return
        self.render_nodes(self._super_pda.graph_nodes(), stack_head=self._stack_symbol)

    def render_nodes(self, pda_nodes: list[dict], stack_head: str | None = None):
        stack_display = stack_head or self._stack_symbol
        nodes = [
            {
                "id": _STACK_NODE_ID,
                "label": f"Stack\n{stack_display}",
                "color": {"background": "#2a3a55", "border": Color.NODE_DEFAULT_BG.value},
                "shape": "box",
                "size": 30,
                "font": {"size": 13, "color": "#cfe5ff"},
                "x": 0,
                "y": -450,
                "fixed": {"x": True, "y": True},
            },
            *pda_nodes,
        ]
        self.graph_view.set_graph(nodes, self._base_edges, _OPTIONS)

    def render_message(self, message: str):
        self._super_pda = None
        self._base_edges = []
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
