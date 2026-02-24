import os
import json
import copy
from typing import Any

import pyvis
from pyvis.network import Network

from PySide6.QtGui import QColor
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.common.colors import Color

# ── vis.js assets bundled with pyvis – loaded once at import time ─────────────
_PYVIS_LIB = os.path.join(os.path.dirname(pyvis.__file__), "templates", "lib")
_VIS_DIR   = os.path.join(_PYVIS_LIB, "vis-9.1.2")


def load_asset(filename: str) -> str:
    with open(os.path.join(_VIS_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()


_VIS_JS  = load_asset("vis-network.min.js")
_VIS_CSS = load_asset("vis-network.css")

_FLOW_DIAGRAM_OPTIONS = {
    "nodes": {
        "font": {"size": 14, "color": Color.TEXT_WHITE.value, "face": "monospace"},
        "borderWidth": 2,
        "shadow": {"enabled": True, "color": "rgba(0,0,0,0.5)", "size": 8},
    },
    "edges": {
        "color": {"color": Color.FLOW_EDGE.value},
        "font": {"size": 11, "color": Color.FLOW_EDGE_FONT.value, "strokeWidth": 0, "align": "middle"},
        "arrows": {"to": {"enabled": True, "scaleFactor": 0.9}},
        "smooth": {"type": "cubicBezier", "forceDirection": "vertical", "roundness": 0.4},
    },
    "layout": {
        "hierarchical": {
            "enabled": True,
            "direction": "UD",
            "sortMethod": "directed",
            "nodeSpacing": 130,
            "levelSeparation": 100,
        }
    },
    "physics": {"enabled": False},
    "interaction": {"dragNodes": False, "zoomView": False, "dragView": False},
}

_SUPER_PDA_OPTIONS = {
    "nodes": {
        "font": {"size": 15, "color": Color.TEXT_WHITE.value},
        "borderWidth": 3,
        "shadow": {"enabled": True},
    },
    "edges": {
        "font": {"size": 10, "color": Color.EDGE_FONT_MUTED.value, "strokeWidth": 0},
        "color": {"color": Color.EDGE_NEUTRAL.value},
        "smooth": {"type": "curvedCW", "roundness": 0.25},
        "arrows": {"to": {"enabled": True, "scaleFactor": 0.8}},
    },
    "physics": {"enabled": False},
}


def js_string(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def extract_options(options: Any) -> dict[str, Any]:
    if options is None:
        return {}

    if isinstance(options, dict):
        return options

    if isinstance(options, str):
        try:
            parsed = json.loads(options)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    to_json = getattr(options, "to_json", None)
    if callable(to_json):
        try:
            parsed = json.loads(to_json())
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}

    return {}


_BASE_HTML = f"""<!DOCTYPE html>
<html>
<head>
<meta charset=\"utf-8\" />
<style>
html, body {{
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: __BG__;
}}
#mynetwork {{
    width: 100%;
    height: 100%;
    background: __BG__;
}}
{_VIS_CSS}
</style>
<script>
{_VIS_JS}
</script>
</head>
<body>
<div id=\"mynetwork\"></div>
<script>
window.__network = null;

function renderGraph(nodes, edges, options) {{
    const container = document.getElementById("mynetwork");
    const data = {{
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
    }};

    if (window.__network) {{
        window.__network.destroy();
    }}

    window.__network = new vis.Network(container, data, options || {{}});
}}
</script>
</body>
</html>
"""


class _SilentPage(QWebEnginePage):
    """QWebEnginePage that suppresses known-harmless JS console messages."""

    _SUPPRESSED: frozenset[str] = frozenset({
        "ResizeObserver loop completed with undelivered notifications.",
    })

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if message not in self._SUPPRESSED:
            super().javaScriptConsoleMessage(level, message, lineNumber, sourceId)


class VisHtmlView(QWidget):
    """
    Generic widget that renders vis.js graphs inside a QWebEngineView.

    Parameters
    ----------
    bg_color : str
        CSS colour string used for the Qt page background and graph canvas.
    parent : QWidget | None
    """

    def __init__(self, bg_color: str = Color.GRAPH_BACKGROUND_DARK.value, parent: QWidget | None = None):
        super().__init__(parent)
        self._bg = bg_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.setPage(_SilentPage(self.web_view))
        self.web_view.page().setBackgroundColor(QColor(bg_color))
        layout.addWidget(self.web_view)

        self._loaded = False
        self._pending_graph: tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]] | None = None
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.web_view.setHtml(_BASE_HTML.replace("__BG__", self._bg))

    # ── public API ────────────────────────────────────────────────────────────

    def on_load_finished(self, ok: bool) -> None:
        self._loaded = ok
        if ok and self._pending_graph is not None:
            nodes, edges, options = self._pending_graph
            self._pending_graph = None
            self.render_graph(nodes, edges, options)

    def render_graph(self, nodes: list[dict[str, Any]], edges: list[dict[str, Any]], options: dict[str, Any]) -> None:
        js = (
            "renderGraph("
            f"{js_string(nodes)},"
            f"{js_string(edges)},"
            f"{js_string(options)}"
            ");"
        )
        self.web_view.page().runJavaScript(js)

    def set_graph(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        options: dict[str, Any] | None = None,
    ) -> None:
        """
        Render a graph from JSON-serialisable vis-network node/edge data.
        """
        resolved_options = options or {}
        if self._loaded:
            self.render_graph(nodes, edges, resolved_options)
            return
        self._pending_graph = (nodes, edges, resolved_options)

    def set_graph_from_net(self, net: Network) -> None:
        """
        Render a pyvis *Network* without generating or patching HTML.
        """
        nodes = list(net.nodes)
        edges = list(net.edges)
        options = extract_options(getattr(net, "options", None))
        self.set_graph(nodes, edges, options)

    def run_js(self, js: str) -> None:
        """Run *js* in the currently loaded page."""
        self.web_view.page().runJavaScript(js)

    @staticmethod
    def apply_flow_diagram_options(net: Network) -> None:
        net.set_options(json.dumps(_FLOW_DIAGRAM_OPTIONS))

    @staticmethod
    def super_pda_options() -> dict[str, Any]:
        return copy.deepcopy(_SUPER_PDA_OPTIONS)
