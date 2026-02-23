"""
stack_graph.py - Stack visualisation as a vertical node chain using Pyvis + QWebEngineView.

The stack is shown top-to-bottom.  The top-of-stack node is highlighted in gold.
A full HTML rebuild is triggered on every update_stack() call (the graph is tiny).
"""

import os
import re
import shutil
import tempfile

import pyvis
from pyvis.network import Network

from PySide6.QtCore import QUrl
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout

_PYVIS_LIB = os.path.join(os.path.dirname(pyvis.__file__), "templates", "lib")
_VIS_DIR   = os.path.join(_PYVIS_LIB, "vis-9.1.2")

_BG      = "#1a1a2a"
_COL_TOP = {"background": "#FFD700", "border": "#B8860B"}
_COL_MID = {"background": "#2a3a5a", "border": "#4A70AA"}
_COL_BOT = {"background": "#1e2a3e", "border": "#334466"}

_OPTIONS = """{
  "nodes": {
    "font": { "size": 14, "color": "#ffffff", "face": "monospace" },
    "borderWidth": 2,
    "shape": "box",
    "shadow": { "enabled": true }
  },
  "edges": {
    "color": { "color": "#445566" },
    "arrows": { "to": { "enabled": true, "scaleFactor": 0.7 } },
    "smooth": { "type": "straightCross" }
  },
  "layout": {
    "hierarchical": {
      "enabled": true,
      "direction": "UD",
      "nodeSpacing": 60,
      "levelSeparation": 70
    }
  },
  "physics": { "enabled": false },
  "interaction": { "dragNodes": false, "zoomView": false, "dragView": false }
}"""

_STYLE = (
    "<style>"
    f"html,body{{margin:0;padding:0;height:100%;background:{_BG};overflow:hidden;}}"
    "#mynetwork{width:100% !important;height:100% !important;}"
    ".vis-network{background:transparent!important;}"
    "canvas{background:transparent!important;}"
    "</style>"
)


class _SilentPage(QWebEnginePage):
    _SUPPRESSED = {"ResizeObserver loop completed with undelivered notifications."}
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if message not in self._SUPPRESSED:
            super().javaScriptConsoleMessage(level, message, lineNumber, sourceId)


class StackGraph(QWidget):
    """Renders the PDA stack as a top-to-bottom node chain."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.setPage(_SilentPage(self.web_view))
        layout.addWidget(self.web_view)

        self._out_dir = os.path.join(tempfile.gettempdir(), "stack_graph")
        os.makedirs(self._out_dir, exist_ok=True)
        for fname in ("vis-network.min.js", "vis-network.css"):
            dst = os.path.join(self._out_dir, fname)
            if not os.path.exists(dst):
                shutil.copy(os.path.join(_VIS_DIR, fname), dst)

        self._html_path = os.path.join(self._out_dir, "stack.html")
        self.update_stack([])          # render empty placeholder on start

    # ── public API ────────────────────────────────────────────────────────────

    def update_stack(self, stack: list):
        """
        Rebuild and reload the stack graph.
        stack should be in bottom-to-top order (PushdownAutomataModel.stack order);
        this widget reverses it so the top-of-stack appears at the top visually.
        """
        html = self._build_html(list(reversed(stack)))   # index 0 = top of stack
        with open(self._html_path, "w", encoding="utf-8") as f:
            f.write(html)
        self.web_view.load(QUrl.fromLocalFile(self._html_path))

    # ── private ───────────────────────────────────────────────────────────────

    def _build_html(self, stack_top_first: list) -> str:
        net = Network(height="100%", width="100%", directed=True, notebook=False, bgcolor=_BG)
        net.set_options(_OPTIONS)

        if not stack_top_first:
            net.add_node("empty", label="\u2205 empty", color=_COL_BOT, size=22, level=0)
        else:
            for i, sym in enumerate(stack_top_first):
                label = f"\u25bc {sym}" if i == 0 else sym
                color = _COL_TOP if i == 0 else (_COL_MID if i < len(stack_top_first) - 1 else _COL_BOT)
                net.add_node(f"s{i}", label=label, color=color, size=22, level=i)
            for i in range(len(stack_top_first) - 1):
                net.add_edge(f"s{i}", f"s{i+1}", label="")

        tmp = os.path.join(self._out_dir, "_tmp.html")
        net.save_graph(tmp)
        with open(tmp, "r", encoding="utf-8") as f:
            html = f.read()

        html = re.sub(
            r"<script[^>]*cdnjs\.cloudflare\.com/ajax/libs/vis-network[^>]*></script>",
            '<script src="vis-network.min.js"></script>',
            html,
        )
        html = html.replace(
            "<body>",
            f"<body style='margin:0;padding:0;background:{_BG};height:100vh;overflow:hidden'>",
            1,
        )
        html = html.replace("</head>", _STYLE + "\n</head>", 1)

        # Title label above the graph
        title = (
            f"<div style='text-align:center;color:#aaa;font-size:11px;font-family:monospace;"
            f"padding:4px 0;border-bottom:1px solid #333;background:{_BG};flex:0 0 auto'>"
            f"STACK &nbsp; (top \u2193)</div>"
        )
        html = html.replace("<body", "<body", 1)  # no-op, just prep
        # Inject title at start of body
        html = re.sub(r"<body([^>]*)>", lambda m: f"<body{m.group(1)}>" + title, html, count=1)

        return html
