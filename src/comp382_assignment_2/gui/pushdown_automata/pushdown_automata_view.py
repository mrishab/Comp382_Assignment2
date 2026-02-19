"""
PDA View — renders the state graph and stack using NetworkX + Pyvis + QWebEngineView.
No Matplotlib. Stack is drawn as an HTML section below the graph.
Uses the locally bundled vis.js from pyvis so it works offline in QWebEngineView.

Two-phase rendering:
  1. render_graph(model) — full rebuild: generates the Pyvis network HTML.
     Called only when the PDA itself changes (dropdown selection).
  2. update_state(model) — lightweight update: patches the info bar and stack
     via JavaScript injection.  Called on each simulation step.
"""

import os
import re
import shutil
import tempfile
import pyvis
import networkx as nx
from pyvis.network import Network
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QUrl

# ── Local vis.js path (ships with pyvis) ────────────────────────────────────
_PYVIS_LIB = os.path.join(os.path.dirname(pyvis.__file__), "templates", "lib")
_VIS_DIR = os.path.join(_PYVIS_LIB, "vis-9.1.2")  # folder with vis-network.min.js

# ── Colour palette ───────────────────────────────────────────────────────────
_COL = {
    "default": {"background": "#4A90D9", "border": "#2C5F8A"},
    "active": {"background": "#FFD700", "border": "#B8860B"},
    "accept": {"background": "#5CB85C", "border": "#3A7A3A"},
    "initial": {"background": "#9B59B6", "border": "#6C3483"},
    "stuck": {"background": "#E74C3C", "border": "#922B21"},
}

_BG_COLOR = "#1a1a2a"

_PYVIS_OPTIONS = """{
  "nodes": {
    "font": { "size": 16, "color": "#ffffff" },
    "borderWidth": 3,
    "shadow": { "enabled": true }
  },
  "edges": {
    "font": { "size": 11, "color": "#eeeeee", "strokeWidth": 0 },
    "color": { "color": "#888888" },
    "smooth": { "type": "curvedCW", "roundness": 0.25 },
    "arrows": { "to": { "enabled": true, "scaleFactor": 0.8 } }
  },
  "physics": {
    "solver": "forceAtlas2Based",
    "forceAtlas2Based": {
      "gravitationalConstant": -100,
      "centralGravity": 0.01,
      "springLength": 150,
      "springConstant": 0.05
    },
    "stabilization": { "iterations": 200, "fit": true }
  }
}"""


def _escape_js(s: str) -> str:
    """Escape a string for safe embedding inside a JS string literal."""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")


class PushdownAutomataView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Output directory — the HTML file lives here alongside vis.js
        self._out_dir = os.path.join(tempfile.gettempdir(), "pda_view")
        os.makedirs(self._out_dir, exist_ok=True)

        # Copy vis.js assets next to the output HTML so file:// works offline
        dest_vis = os.path.join(self._out_dir, "vis-network.min.js")
        dest_css = os.path.join(self._out_dir, "vis-network.css")
        if not os.path.exists(dest_vis):
            shutil.copy(os.path.join(_VIS_DIR, "vis-network.min.js"), dest_vis)
        if not os.path.exists(dest_css):
            shutil.copy(os.path.join(_VIS_DIR, "vis-network.css"), dest_css)

        self._html_path = os.path.join(self._out_dir, "pda_graph.html")
        self._page_loaded = False

    # ── public API ───────────────────────────────────────────────────────────

    def render_graph(self, model):
        """Full page rebuild — call when the PDA changes (dropdown selection)."""
        html = self._render_full(model)
        with open(self._html_path, "w", encoding="utf-8") as f:
            f.write(html)
        self._page_loaded = False
        self.web_view.loadFinished.connect(self._on_page_loaded)
        self.web_view.load(QUrl.fromLocalFile(self._html_path))

    def update_state(self, model):
        """Lightweight update — patches info bar + stack via JS. No page reload."""
        if not self._page_loaded:
            # Page hasn't finished loading yet; fall back to full render
            self.render_graph(model)
            return
        js = self._build_state_update_js(model)
        self.web_view.page().runJavaScript(js)

    # Back-compat: old code calls update_view
    def update_view(self, model):
        self.update_state(model)

    # ── private slots ────────────────────────────────────────────────────────

    def _on_page_loaded(self, ok: bool):
        self._page_loaded = ok
        try:
            self.web_view.loadFinished.disconnect(self._on_page_loaded)
        except RuntimeError:
            pass

    # ── graph building ───────────────────────────────────────────────────────

    def _build_nx_graph(self, model):
        """Build a NetworkX MultiDiGraph from the PDA and aggregate edge labels."""
        G = nx.MultiDiGraph()
        for state in model.states:
            G.add_node(state)

        edge_labels: dict[tuple, list[str]] = {}
        for (src, char, top), trans_list in model.transitions.items():
            for dst, push in trans_list:
                label = f"{char or 'ε'},{top or 'ε'} → {''.join(push) if push else 'ε'}"
                edge_labels.setdefault((src, dst), []).append(label)

        for (u, v), labels in edge_labels.items():
            G.add_edge(u, v, label=" | ".join(labels))

        return G, edge_labels

    def _pyvis_from_nx(self, model, G, edge_labels) -> str:
        """Generate Pyvis HTML using local vis.js, return the HTML string."""
        net = Network(
            height="100%",
            width="100%",
            directed=True,
            notebook=False,
            bgcolor=_BG_COLOR,
        )
        net.set_options(_PYVIS_OPTIONS)

        stuck = model.is_stuck()
        for node in G.nodes():
            if node == model.current_state:
                col = _COL["stuck"] if stuck else _COL["active"]
            elif node in model.final_states and node == model.initial_state:
                col = _COL["initial"]
            elif node in model.final_states:
                col = _COL["accept"]
            elif node == model.initial_state:
                col = _COL["initial"]
            else:
                col = _COL["default"]

            net.add_node(
                node,
                label=node,
                color=col,
                shape="doublecircle" if node in model.final_states else "circle",
                size=30,
            )

        for (u, v), labels in edge_labels.items():
            net.add_edge(u, v, label=" | ".join(labels))

        # Save Pyvis HTML to a temp file, then read it back
        tmp = os.path.join(self._out_dir, "_tmp_net.html")
        net.save_graph(tmp)
        with open(tmp, "r", encoding="utf-8") as f:
            return f.read()

    # ── HTML composition ─────────────────────────────────────────────────────

    def _stack_html(self, model) -> str:
        stack = list(reversed(model.stack))
        if not stack:
            items = "<span style='color:#888;font-style:italic'>empty</span>"
        else:
            items = "".join(
                f"<span style='display:inline-block;background:{'#FFD700' if i == 0 else '#2a2a3a'};"
                f"color:{'#000' if i == 0 else '#eee'};padding:3px 10px;margin:0 2px;"
                f"border-radius:4px;border:1px solid #555;font-family:monospace;font-size:13px'>"
                f"{'▶ ' if i == 0 else ''}{sym}</span>"
                for i, sym in enumerate(stack)
            )
        return (
            f"<div style='color:#aaa;font-size:11px;margin-bottom:4px'>STACK (top first →)</div>"
            f"<div style='display:flex;flex-wrap:wrap;align-items:center;gap:2px'>{items}</div>"
        )

    def _info_html(self, model) -> str:
        consumed = model.input_string[: model.input_index] or "(none)"
        remaining = model.input_string[model.input_index :] or "(done)"

        if model.is_accepted():
            badge = "<span style='color:#5CB85C;font-weight:bold'>Accepted</span>"
        elif model.is_stuck():
            badge = (
                "<span style='color:#E74C3C;font-weight:bold'>Rejected / Stuck</span>"
            )
        else:
            badge = f"<span style='color:#FFD700'>State: <b>{model.current_state}</b></span>"

        return (
            f"<div style='display:flex;align-items:center;gap:20px;flex-wrap:wrap'>"
            f"  <div>"
            f"    <div>Consumed: <code style='color:#80ff80'>{consumed}</code></div>"
            f"    <div>Remaining: <code style='color:#ff8080'>{remaining}</code></div>"
            f"  </div>"
            f"  <div style='margin-left:auto'>{badge}</div>"
            f"</div>"
        )

    def _render_full(self, model) -> str:
        G, edge_labels = self._build_nx_graph(model)
        graph_html = self._pyvis_from_nx(model, G, edge_labels)

        bottom_bar = f"""
        <div id="pda-bottom-bar" style='background:{_BG_COLOR};color:#eee;font-family:sans-serif;
                    padding:8px 14px;border-top:1px solid #333;font-size:13px'>
          <div id="pda-info" style="margin-bottom:6px">
            {self._info_html(model)}
          </div>
          <div id="pda-stack">
            {self._stack_html(model)}
          </div>
        </div>
        """

        # Strip the CDN script tag → use local vis.js
        html = re.sub(
            r"<script[^>]*cdnjs\.cloudflare\.com/ajax/libs/vis-network[^>]*></script>",
            '<script src="vis-network.min.js"></script>',
            graph_html,
        )

        # Make the vis.js canvas container fill available space above the bottom bar.
        # Pyvis generates a div with id="mynetwork" — restyle it.
        html = html.replace(
            "<body>",
            f"<body style='background:{_BG_COLOR};margin:0;display:flex;flex-direction:column;height:100vh;overflow:hidden'>\n",
            1,
        )

        # Make the #mynetwork div expand to fill remaining space
        html = re.sub(
            r'(style\s*=\s*"[^"]*)(width:\s*\d+[^;]*;)([^"]*)(height:\s*\d+[^;]*;)',
            r"\1width:100%;\3height:100%;",
            html,
            count=1,
        )

        # Wrap #mynetwork in a flex-growing container and append bottom bar before </body>
        html = html.replace(
            "</body>",
            bottom_bar + "\n</body>",
            1,
        )

        # Ensure the mynetwork div grows (inject a style block)
        style_inject = f"""
        <style>
          html, body {{ margin:0; padding:0; height:100%; background:{_BG_COLOR}; }}
          #mynetwork {{ flex:1 1 auto; min-height:0; }}
          #pda-bottom-bar {{ flex:0 0 auto; }}
          .vis-network {{ background: transparent !important; }}
          canvas {{ background: transparent !important; }}
        </style>
        """
        html = html.replace("</head>", style_inject + "\n</head>", 1)

        return html

    # ── JS-based lightweight state update ─────────────────────────────────────

    def _build_state_update_js(self, model) -> str:
        info_html = _escape_js(self._info_html(model))
        stack_html = _escape_js(self._stack_html(model))
        return (
            f"document.getElementById('pda-info').innerHTML = '{info_html}';"
            f"document.getElementById('pda-stack').innerHTML = '{stack_html}';"
        )
