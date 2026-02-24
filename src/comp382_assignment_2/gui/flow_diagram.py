import os
import re
import tempfile

import networkx as nx
import pyvis
from pyvis.network import Network

from PySide6.QtGui import QColor
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout

# ── vis.js local assets (shipped with pyvis) ─────────────────────────────────
_PYVIS_LIB = os.path.join(os.path.dirname(pyvis.__file__), "templates", "lib")
_VIS_DIR   = os.path.join(_PYVIS_LIB, "vis-9.1.2")


def _load_asset(filename: str) -> str:
    with open(os.path.join(_VIS_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()


# Read once at import time so render() never touches the filesystem.
_VIS_JS  = _load_asset("vis-network.min.js")
_VIS_CSS = _load_asset("vis-network.css")

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

_STYLE_INJECT = (
    "<style>\n"
    "  html, body { margin:0; padding:0; width:100%; height:100vh;"
    " background:#1a1a2a; overflow:hidden; }\n"
    "  #mynetwork { width:100% !important; height:100vh !important; }\n"
    "  .vis-network { background: #1a1a2a !important; }\n"
    "  canvas { background: #1a1a2a !important; }\n"
    "</style>\n"
)


class _SilentPage(QWebEnginePage):
    _SUPPRESSED = {"ResizeObserver loop completed with undelivered notifications."}

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if message not in self._SUPPRESSED:
            super().javaScriptConsoleMessage(level, message, lineNumber, sourceId)


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

        self.web_view = QWebEngineView()
        self.web_view.setPage(_SilentPage(self.web_view))
        self.web_view.page().setBackgroundColor(QColor("#1a1a2a"))
        layout.addWidget(self.web_view)

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

    def _net_to_html(self, net: Network) -> str:
        """Return pyvis HTML as a string without leaving any files on disk."""
        if hasattr(net, "generate_html"):
            # Available in pyvis ≥ 0.7; returns a self-contained HTML string.
            return net.generate_html()
        # Fallback: write to a temp file, read, then delete immediately.
        fd, tmp_path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        try:
            net.save_graph(tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                return f.read()
        finally:
            os.unlink(tmp_path)

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
        G.add_edge("Input",    "Language", label=self.input_value)
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

        # ── build HTML entirely in-memory ────────────────────────────────────
        html = self._net_to_html(net)

        # Replace CDN vis-network <script> with the inlined bundle.
        # Use a lambda so backslashes in the JS source are never interpreted
        # as regex replacement escape sequences.
        _js_block  = f"<script>\n{_VIS_JS}\n</script>"
        _css_block = f"<style>\n{_VIS_CSS}\n</style>"
        html = re.sub(
            r"<script[^>]*cdnjs\.cloudflare\.com[^>]*vis-network[^>]*></script>",
            lambda _: _js_block,
            html,
        )
        # Replace CDN vis-network <link> with inlined CSS.
        html = re.sub(
            r'<link[^>]*cdnjs\.cloudflare\.com[^>]*vis-network[^>]*/?>',
            lambda _: _css_block,
            html,
        )

        # Transparent body (overrides any pyvis default background).
        html = html.replace(
            "<body>",
            "<body style='margin:0;padding:0;background:#1a1a2a;height:100vh;overflow:hidden'>",
            1,
        )
        html = html.replace("</head>", _STYLE_INJECT + "</head>", 1)

        # Load entirely from memory — no file:// URL needed.
        self.web_view.setHtml(html)
