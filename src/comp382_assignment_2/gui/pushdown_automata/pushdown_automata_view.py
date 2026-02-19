"""
PDA View — renders the state graph and stack using NetworkX + Pyvis + QWebEngineView.
No Matplotlib. Stack is drawn as an HTML table embedded in the Pyvis page.
Uses the locally bundled vis.js from pyvis so it works offline in QWebEngineView.
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
_VIS_DIR   = os.path.join(_PYVIS_LIB, "vis-9.1.2")   # folder with vis-network.min.js

# ── Colour palette ───────────────────────────────────────────────────────────
_COL = {
    "default": {"background": "#4A90D9", "border": "#2C5F8A"},
    "active":  {"background": "#FFD700", "border": "#B8860B"},
    "accept":  {"background": "#5CB85C", "border": "#3A7A3A"},
    "initial": {"background": "#9B59B6", "border": "#6C3483"},
    "stuck":   {"background": "#E74C3C", "border": "#922B21"},
}

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


class PushdownAutomataView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # Output directory — the HTML file lives here alongside vis.js symlink
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

    # ── public ──────────────────────────────────────────────────────────────

    def update_view(self, model):
        html = self._render(model)
        with open(self._html_path, "w", encoding="utf-8") as f:
            f.write(html)
        self.web_view.load(QUrl.fromLocalFile(self._html_path))

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
        net = Network(height="420px", width="100%", directed=True, notebook=False)
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
                node, label=node, color=col,
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

    # ── HTML composition ────────────────────────────────────────────────────

    def _stack_html(self, model) -> str:
        stack = list(reversed(model.stack))
        if not stack:
            rows = "<li style='color:#888;font-style:italic;padding:4px 16px'>empty</li>"
        else:
            rows = "".join(
                f"<li style='background:{'#FFD700' if i == 0 else '#2a2a3a'};"
                f"color:{'#000' if i == 0 else '#eee'};padding:4px 20px;"
                f"border-bottom:1px solid #444'>"
                f"{'▶ ' if i == 0 else '&#8288; '}{sym}</li>"
                for i, sym in enumerate(stack)
            )
        return f"""
        <div style='display:inline-block;margin:6px 12px;vertical-align:top'>
          <div style='color:#aaa;font-size:11px;margin-bottom:3px'>STACK (top ↓)</div>
          <ul style='list-style:none;padding:0;margin:0;border:1px solid #555;
                     border-radius:6px;overflow:hidden;font-family:monospace;font-size:14px'>
            {rows}
          </ul>
        </div>"""

    def _render(self, model) -> str:
        G, edge_labels = self._build_nx_graph(model)
        graph_html     = self._pyvis_from_nx(model, G, edge_labels)

        consumed  = model.input_string[:model.input_index] or "(none)"
        remaining = model.input_string[model.input_index:] or "(done)"

        if model.is_accepted():
            badge = "<span style='color:#5CB85C;font-weight:bold'>✅ Accepted</span>"
        elif model.is_stuck():
            badge = "<span style='color:#E74C3C;font-weight:bold'>❌ Rejected / Stuck</span>"
        else:
            badge = f"<span style='color:#FFD700'>🔄 Running — state: <b>{model.current_state}</b></span>"

        info_bar = f"""
        <div style='background:#111827;color:#eee;font-family:sans-serif;
                    padding:6px 14px;border-bottom:1px solid #333;font-size:13px;
                    display:flex;align-items:center;gap:20px;flex-wrap:wrap'>
          {self._stack_html(model)}
          <div>
            <div>Consumed: <code style='color:#80ff80'>{consumed}</code></div>
            <div>Remaining: <code style='color:#ff8080'>{remaining}</code></div>
          </div>
          <div style='margin-left:auto'>{badge}</div>
        </div>
        <hr style='border:none;border-top:1px solid #333;margin:0'>
        """

        # Strip the CDN script tag (including SRI integrity attr) → use local vis.js
        html = re.sub(
            r'<script[^>]*cdnjs\.cloudflare\.com/ajax/libs/vis-network[^>]*></script>',
            '<script src="vis-network.min.js"></script>',
            graph_html,
        )

        # Inject info bar right after <body>
        html = html.replace(
            "<body>",
            "<body style='background:#1e1e2e;margin:0'>\n" + info_bar,
            1,
        )
        return html