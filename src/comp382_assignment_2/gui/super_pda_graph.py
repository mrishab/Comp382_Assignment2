"""
super_pda_graph.py - PDA state-machine visualisation using PDABuilder + QWebEngineView.

Public API
----------
render_graph(config)  Full rebuild from a raw pda.json config dict.
update_state(model)   Lightweight JS update: recolours nodes + patches info bar.
                      No page reload - uses vis.js DataSet.update() directly.
"""

import json
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

from comp382_assignment_2.gui.pda_builder import PDABuilder

# ── vis.js local assets ───────────────────────────────────────────────────────
_PYVIS_LIB = os.path.join(os.path.dirname(pyvis.__file__), "templates", "lib")
_VIS_DIR   = os.path.join(_PYVIS_LIB, "vis-9.1.2")

_BG = "#1a1a2a"

_PYVIS_OPTIONS = """{
  "nodes": {
    "font": { "size": 15, "color": "#ffffff" },
    "borderWidth": 3,
    "shadow": { "enabled": true }
  },
  "edges": {
    "font": { "size": 10, "color": "#dddddd", "strokeWidth": 0 },
    "color": { "color": "#667799" },
    "smooth": { "type": "curvedCW", "roundness": 0.25 },
    "arrows": { "to": { "enabled": true, "scaleFactor": 0.8 } }
  },
  "physics": {
    "solver": "forceAtlas2Based",
    "forceAtlas2Based": {
      "gravitationalConstant": -80,
      "centralGravity": 0.01,
      "springLength": 140,
      "springConstant": 0.05
    },
    "stabilization": { "iterations": 200, "fit": true }
  }
}"""


def _esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\\'").replace("\n", "\\n")


class _SilentPage(QWebEnginePage):
    _SUPPRESSED = {"ResizeObserver loop completed with undelivered notifications."}
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceId):
        if message not in self._SUPPRESSED:
            super().javaScriptConsoleMessage(level, message, lineNumber, sourceId)


class SuperPDAGraph(QWidget):
    """Renders the PDA state machine and live-updates the active state via JS."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.setPage(_SilentPage(self.web_view))
        layout.addWidget(self.web_view)

        self._out_dir = os.path.join(tempfile.gettempdir(), "super_pda_graph")
        os.makedirs(self._out_dir, exist_ok=True)
        for fname in ("vis-network.min.js", "vis-network.css"):
            dst = os.path.join(self._out_dir, fname)
            if not os.path.exists(dst):
                shutil.copy(os.path.join(_VIS_DIR, fname), dst)

        self._html_path = os.path.join(self._out_dir, "pda.html")
        self._page_loaded = False
        self._model = None
        self._builder: PDABuilder | None = None

        self.render_empty()     # show blank graph on startup

    # ── public API ────────────────────────────────────────────────────────────

    def render_empty(self):
        """Render a blank graph with a hint label. Called on startup."""
        net = Network(height="100%", width="100%", directed=True, notebook=False, bgcolor=_BG)
        net.set_options(_PYVIS_OPTIONS)
        # Single invisible anchor node so vis.js initialises cleanly
        net.add_node(
            "hint",
            label="Select languages above\nto load the Super PDA",
            color={"background": "#1e2a3e", "border": "#334466"},
            shape="box",
            size=35,
            font={"size": 14, "color": "#556688"},
        )
        tmp = os.path.join(self._out_dir, "_tmp.html")
        net.save_graph(tmp)
        with open(tmp, "r", encoding="utf-8") as f:
            html = f.read()
        html = self._patch_html(html, info_html="")
        with open(self._html_path, "w", encoding="utf-8") as f:
            f.write(html)
        self._page_loaded = False
        self.web_view.load(QUrl.fromLocalFile(self._html_path))

    def render_graph(self, config: dict):
        """Full page rebuild from a pda.json config dict."""
        self._builder = PDABuilder(config)
        self._model = None
        net = self._builder.build_pyvis_network(
            bgcolor=_BG, options=_PYVIS_OPTIONS
        )
        tmp = os.path.join(self._out_dir, "_tmp.html")
        net.save_graph(tmp)
        with open(tmp, "r", encoding="utf-8") as f:
            html = f.read()
        html = self._patch_html(html, info_html="")
        with open(self._html_path, "w", encoding="utf-8") as f:
            f.write(html)
        self._page_loaded = False
        try:
            self.web_view.loadFinished.disconnect(self._on_loaded)
        except RuntimeError:
            pass
        self.web_view.loadFinished.connect(self._on_loaded)
        self.web_view.load(QUrl.fromLocalFile(self._html_path))

    # ── shared HTML patching ──────────────────────────────────────────────────

    def _patch_html(self, html: str, info_html: str) -> str:
        """Apply common HTML post-processing: local vis.js, body style, info bar, CSS."""
        import re as _re
        html = _re.sub(
            r"<script[^>]*cdnjs\.cloudflare\.com/ajax/libs/vis-network[^>]*></script>",
            '<script src="vis-network.min.js"></script>',
            html,
        )
        html = html.replace(
            "<body>",
            f"<body style='margin:0;padding:0;background:{_BG};'>",
            1,
        )
        if info_html is not None:
            visibility = "" if info_html else "display:none;"
            bar = (
                f"<div id='pda-info' style='background:{_BG};color:#eee;font-family:sans-serif;"
                f"padding:6px 12px;border-top:1px solid #333;font-size:12px;flex:0 0 auto;{visibility}'>"
                f"{info_html}</div>"
            )
            html = html.replace("</body>", bar + "\n</body>", 1)
        style = (
            "<style>"
            f"html,body{{margin:0;padding:0;height:100vh;background:{_BG};overflow:hidden;display:flex;flex-direction:column;}}"
            "#mynetwork{flex:1 1 auto;min-height:0;width:100% !important;}"
            ".vis-network canvas{background:transparent !important;}"
            "</style>"
            "<script>"
            "document.addEventListener('DOMContentLoaded',function(){"
            "  var _p=setInterval(function(){"
            "    if(typeof network!=='undefined'){"
            "      clearInterval(_p);"
            "      network.redraw();"
            "      network.fit();"
            "      network.on('stabilizationIterationsDone',function(){network.setOptions({physics:{enabled:false}});network.fit();});"
            "      network.on('stabilized',function(){network.setOptions({physics:{enabled:false}});});"
            "    }"
            "  },100);"
            "});"
            "</script>"
        )
        html = html.replace("</head>", style + "\n</head>", 1)
        return html

    def update_state(self, model):
        """Lightweight JS update: recolour nodes + refresh info bar."""
        self._model = model
        if not self._page_loaded or self._builder is None:
            return
        self.web_view.page().runJavaScript(self._state_js(model))

    # Back-compat shim
    def update_view(self, model):
        self.update_state(model)

    # ── private ───────────────────────────────────────────────────────────────

    def _on_loaded(self, ok: bool):
        self._page_loaded = ok
        try:
            self.web_view.loadFinished.disconnect(self._on_loaded)
        except RuntimeError:
            pass
        if ok and self._model and self._builder:
            self.web_view.page().runJavaScript(self._state_js(self._model))

    def _state_js(self, model) -> str:
        updates = [
            {"id": s, "color": self._builder.node_color(s, model)}
            for s in self._builder.states
        ]
        info = _esc(self._info_html(model))
        return (
            f"if(typeof nodes !== 'undefined'){{ nodes.update({json.dumps(updates)}); }}"
            f"var el=document.getElementById('pda-info'); if(el){{ el.style.display=''; el.innerHTML='{info}'; }}"
        )

    def _info_html(self, model) -> str:
        consumed  = model.input_string[:model.input_index]  or "(none)"
        remaining = model.input_string[model.input_index:]  or "(done)"
        if model.is_accepted():
            badge = "<span style='color:#5CB85C;font-weight:bold'>Accepted \u2713</span>"
        elif model.is_stuck():
            badge = "<span style='color:#E74C3C;font-weight:bold'>Rejected / Stuck \u2717</span>"
        else:
            badge = f"<span style='color:#FFD700'>State: <b>{model.current_state}</b></span>"
        return (
            f"<div style='display:flex;align-items:center;gap:16px;flex-wrap:wrap'>"
            f"  <div style='font-size:12px'>"
            f"    <span style='color:#80ff80'>Consumed: <code>{consumed}</code></span> &nbsp; "
            f"    <span style='color:#ff8080'>Remaining: <code>{remaining}</code></span>"
            f"  </div>"
            f"  <div style='margin-left:auto'>{badge}</div>"
            f"</div>"
        )
