from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.gui.html_view import VisHtmlView
from comp382_assignment_2.super_pda.base import BaseSuperPDA
from comp382_assignment_2.super_pda.stack_view import StackView

_BG = Color.GRAPH_BACKGROUND_DARK.value


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
        stack_view = getattr(super_pda, "stack_view", None)
        self.render_nodes(super_pda.graph_nodes(), stack_view=stack_view)

    def update_state(self, model):
        if self._super_pda is None:
            return
        nodes = self._super_pda.graph_nodes(model=model)
        stack_view = getattr(model, "stack_view", None)
        self.render_nodes(nodes, stack_view=stack_view)

    def reset_state(self):
        if self._super_pda is None:
            return
        stack_view = getattr(self._super_pda, "stack_view", None)
        self.render_nodes(self._super_pda.graph_nodes(), stack_view=stack_view)

    def render_nodes(self, pda_nodes: list[dict], stack_view: StackView | None = None):
        active_stack_view = stack_view or StackView()
        if stack_view is None:
            active_stack_view.reset([self._stack_symbol])
        nodes = [*active_stack_view.nodes(), *pda_nodes]
        edges = [*active_stack_view.edges(), *self._base_edges]
        self.graph_view.set_graph(nodes, edges, VisHtmlView.super_pda_options())

    def render_message(self, message: str):
        self._super_pda = None
        self._base_edges = []
        nodes = [{
            "id": "hint",
            "label": message,
            "color": {"background": Color.SUPER_HINT_BG.value, "border": Color.SUPER_HINT_BORDER.value},
            "shape": "box",
            "size": 35,
            "font": {"size": 14, "color": Color.SUPER_HINT_TEXT.value},
        }]
        edges = []
        options = VisHtmlView.super_pda_options()
        self.graph_view.set_graph(nodes, edges, options)
