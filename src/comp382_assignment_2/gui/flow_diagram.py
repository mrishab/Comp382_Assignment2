import networkx as nx
from pyvis.network import Network
from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.gui.html_view import VisHtmlView

_BG = "#1a1a2a"

_COL = {
    "idle":   {"background": "#4A4A6A", "border": "#7070AA"},
    "accept": {"background": "#5CB85C", "border": "#3A7A3A"},
    "reject": {"background": "#E74C3C", "border": "#922B21"},
    "gate":   {"background": "#2d6a4f", "border": "#40916c"},
    "input":  {"background": "#4A90D9", "border": "#2C5F8A"},
    "result": {"background": "#22304A", "border": "#5a7eaa"},
    "lang":   {"background": "#1e2a3e", "border": "#4A90D9"},
    "start":  {"background": "#6A4A8A", "border": "#9A70BB"},
}

_OPTIONS = """{
  "nodes": {
    "font": { "size": 14, "color": "#ffffff", "face": "monospace" },
    "borderWidth": 2,
    "shadow": { "enabled": true, "color": "rgba(0,0,0,0.5)", "size": 8 }
  },
  "edges": {
    "color": { "color": "#5a7eaa" },
    "font": { "size": 11, "color": "#aaaacc", "strokeWidth": 0, "align": "middle" },
    "arrows": { "to": { "enabled": true, "scaleFactor": 0.9 } },
    "smooth": { "type": "cubicBezier", "forceDirection": "vertical", "roundness": 0.4 }
  },
  "layout": {
    "hierarchical": {
      "enabled": true,
      "direction": "UD",
      "sortMethod": "directed",
      "nodeSpacing": 130,
      "levelSeparation": 100
    }
  },
  "physics": { "enabled": false },
  "interaction": { "dragNodes": false, "zoomView": false, "dragView": false }
}"""

class FlowDiagram(QWidget):
    """
    Pipeline diagram:
      selected_regex → DFA ──┐
                              ├→ ∩ Gate → Language → Result
      selected_cfl   → PDA ──┘       ↑
                                    Input
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.view = VisHtmlView(bg_color=_BG)
        layout.addWidget(self.view)

        # ── Public state (mutated by main_panel before calling update()) ──────
        self.gate_status:    str        = ""
        self.result_text:    str        = ""
        self.dfa_status:     bool | None = None
        self.pda_status:     bool | None = None
        self.language_label: str        = ""
        self.selected_regex: str        = ""
        self.selected_cfl:   str        = ""
        self.input_value:    str        = ""

        self.render()

    # ── public API ────────────────────────────────────────────────────────────

    def update(self):
        """Re-render the pyvis graph (called by main_panel after state changes)."""
        self.render()

    # ── private ───────────────────────────────────────────────────────────────────

    def _status_color(self, status: bool | None) -> dict:
        if status is True:
            return _COL["accept"]
        if status is False:
            return _COL["reject"]
        return _COL["idle"]

    def _edge_label(self, status: bool | None) -> str:
        if status is True:
            return "✓"
        if status is False:
            return "✗"
        return ""

    def render(self):
        # ── node labels ──────────────────────────────────────────────────────
        regex_label  = self.selected_regex or "Regex"
        cfl_label    = self.selected_cfl   or "CFL"
        input_label  = self.input_value    or "Input"
        gate_label   = self.gate_status    or "∩ Gate"
        lang_label   = self.language_label or "Language"
        result_label = self.result_text    or "Result"

        # ── graph topology ───────────────────────────────────────────────────
        #   Level 0: selected_regex start node,  selected_cfl start node
        #   Level 1: DFA,                         PDA
        #   Level 2: ∩ Gate,                      Input
        #   Level 3: Language (combined)
        #   Level 4: Result
        G = nx.DiGraph()
        G.add_node("Regex",    level=0)
        G.add_node("CFL",      level=0)
        G.add_node("DFA",      level=1)
        G.add_node("PDA",      level=1)
        G.add_node("∩ Gate",   level=2)
        G.add_node("Input",    level=3)
        G.add_node("Language", level=3)
        G.add_node("Result",   level=4)

        G.add_edge("Regex",    "DFA",      label="")
        G.add_edge("CFL",      "PDA",      label="")
        G.add_edge("DFA",      "∩ Gate",   label=self._edge_label(self.dfa_status))
        G.add_edge("PDA",      "∩ Gate",   label=self._edge_label(self.pda_status))
        G.add_edge("∩ Gate",   "Language", label="∩")
        G.add_edge("Input",    "Language", label="")
        G.add_edge("Language", "Result",   label="")

        # ── vis network ──────────────────────────────────────────────────────
        net = Network(height="100%", width="100%", directed=True, notebook=False, bgcolor=_BG)
        net.set_options(_OPTIONS)

        node_defs = {
            "Regex":    (regex_label,  _COL["start"],                        "ellipse", 28),
            "CFL":      (cfl_label,    _COL["start"],                        "ellipse", 28),
            "DFA":      ("DFA",        self._status_color(self.dfa_status),   "ellipse", 32),
            "PDA":      ("PDA",        self._status_color(self.pda_status),   "ellipse", 32),
            "∩ Gate":   (gate_label,   _COL["gate"],                         "box",     30),
            "Input":    (input_label,  _COL["input"],                        "box",     28),
            "Language": (lang_label,   _COL["lang"],                         "box",     28),
            "Result":   (result_label, _COL["result"],                       "box",     30),
        }

        for node_id, (label, color, shape, size) in node_defs.items():
            net.add_node(
                node_id,
                label=label,
                color=color,
                shape=shape,
                size=size,
                level=G.nodes[node_id]["level"],
            )

        for u, v, data in G.edges(data=True):
            net.add_edge(u, v, label=data.get("label", ""))

        # ── render via shared HTML view ───────────────────────────────────────
        self.view.set_graph_from_net(net)
