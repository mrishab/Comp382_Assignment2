import os
import re
import shutil
import tempfile

import networkx as nx
import pyvis
from pyvis.network import Network

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout

# ── vis.js local assets (shipped with pyvis) ────────────────────────────────────────────
_PYVIS_LIB = os.path.join(os.path.dirname(pyvis.__file__), "templates", "lib")
_VIS_DIR = os.path.join(_PYVIS_LIB, "vis-9.1.2")

_BG = "#1a1a2a"

_COL = {
    "idle":   {"background": "#4A4A6A", "border": "#7070AA"},
    "accept": {"background": "#5CB85C", "border": "#3A7A3A"},
    "reject": {"background": "#E74C3C", "border": "#922B21"},
    "gate":   {"background": "#2d6a4f", "border": "#40916c"},
    "input":  {"background": "#4A90D9", "border": "#2C5F8A"},
    "result": {"background": "#22304A", "border": "#5a7eaa"},
    "lang":   {"background": "#1e2a3e", "border": "#4A90D9"},
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
    "  html, body { margin:0; padding:0; height:100%; background:" + "#1a1a2a" + "; overflow:hidden; }\n"
    "  #mynetwork { width:100% !important; height:100% !important; }\n"
    "  .vis-network { background: transparent !important; }\n"
    "  canvas { background: transparent !important; }\n"
    "</style>\n"
)


class _SilentPage(QWebEnginePage):
    _SUPPRESSED = {"ResizeObserver loop completed with undelivered notifications."}

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if message not in self._SUPPRESSED:
            super().javaScriptConsoleMessage(level, message, lineNumber, sourceId)


class FlowDiagram(QWidget):
    """Pipeline diagram: Input → CFA (DFA) / PDA → ∩ Gate → Language → Result."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.setPage(_SilentPage(self.web_view))
        layout.addWidget(self.web_view)

        self._out_dir = os.path.join(tempfile.gettempdir(), "flow_diagram")
        os.makedirs(self._out_dir, exist_ok=True)

        for fname in ("vis-network.min.js", "vis-network.css"):
            dst = os.path.join(self._out_dir, fname)
            if not os.path.exists(dst):
                shutil.copy(os.path.join(_VIS_DIR, fname), dst)

        self._html_path = os.path.join(self._out_dir, "flow.html")

        # ── Public state (mutated by main_panel before calling update()) ──────
        self.gate_status: str = ""
        self.result_text: str = ""
        self.dfa_status: bool | None = None
        self.pda_status: bool | None = None
        self.language_label: str = ""

        self._render()

    # ── public API ────────────────────────────────────────────────────────────

    def update(self):
        """Re-render and reload the pyvis graph (called by main_panel after state changes)."""
        self._render()

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

    def _render(self):
        G = nx.DiGraph()
        G.add_node("Input",    level=0)
        G.add_node("CFA",      level=1)
        G.add_node("PDA",      level=1)
        G.add_node("∩ Gate",   level=2)
        G.add_node("Language", level=3)
        G.add_node("Result",   level=4)

        G.add_edge("Input",    "CFA",        label="regular")
        G.add_edge("Input",    "PDA",        label="context-free")
        G.add_edge("CFA",      "∩ Gate", label=self._edge_label(self.dfa_status))
        G.add_edge("PDA",      "∩ Gate", label=self._edge_label(self.pda_status))
        G.add_edge("∩ Gate",   "Language",  label="")
        G.add_edge("Language", "Result",     label="")

        gate_label   = self.gate_status    or "∩ Gate"
        lang_label   = self.language_label or "Language"
        result_label = self.result_text    or "Result"

        net = Network(height="100%", width="100%", directed=True, notebook=False, bgcolor=_BG)
        net.set_options(_OPTIONS)

        node_defs = {
            "Input":      ("Input",      _COL["input"],                     "box",     28),
            "CFA":        ("CFA (DFA)",  self._status_color(self.dfa_status), "ellipse", 32),
            "PDA":        ("PDA",        self._status_color(self.pda_status), "ellipse", 32),
            "∩ Gate": (gate_label,  _COL["gate"],                      "box",     30),
            "Language":   (lang_label,   _COL["lang"],                      "box",     28),
            "Result":     (result_label, _COL["result"],                    "box",     30),
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

        tmp = os.path.join(self._out_dir, "_tmp.html")
        net.save_graph(tmp)
        with open(tmp, "r", encoding="utf-8") as f:
            html = f.read()

        # Swap CDN vis.js reference for local offline copy
        html = re.sub(
            r"<script[^>]*cdnjs\.cloudflare\.com/ajax/libs/vis-network[^>]*></script>",
            '<script src="vis-network.min.js"></script>',
            html,
        )

        html = html.replace(
            "<body>",
            "<body style='margin:0;padding:0;background:#1a1a2a;height:100vh;overflow:hidden'>",
            1,
        )
        html = html.replace("</head>", _STYLE_INJECT + "</head>", 1)

        with open(self._html_path, "w", encoding="utf-8") as f:
            f.write(html)

        self.web_view.load(QUrl.fromLocalFile(self._html_path))
