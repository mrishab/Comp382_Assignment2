import os
import re
import tempfile

import pyvis
from pyvis.network import Network

from PySide6.QtGui import QColor
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QVBoxLayout

# ── vis.js assets bundled with pyvis – loaded once at import time ─────────────
_PYVIS_LIB = os.path.join(os.path.dirname(pyvis.__file__), "templates", "lib")
_VIS_DIR   = os.path.join(_PYVIS_LIB, "vis-9.1.2")


def _load_asset(filename: str) -> str:
    with open(os.path.join(_VIS_DIR, filename), "r", encoding="utf-8") as f:
        return f.read()


_VIS_JS  = _load_asset("vis-network.min.js")
_VIS_CSS = _load_asset("vis-network.css")

# Inline blocks – built once, reused on every set_html() call.
_JS_BLOCK  = f"<script>\n{_VIS_JS}\n</script>"
_CSS_BLOCK = f"<style>\n{_VIS_CSS}\n</style>"

# Regex patterns for CDN references that pyvis/the caller may emit.
_CDN_SCRIPT_RE = re.compile(
    r"<script[^>]*cdnjs\.cloudflare\.com[^>]*vis-network[^>]*></script>"
)
_CDN_LINK_RE = re.compile(
    r'<link[^>]*cdnjs\.cloudflare\.com[^>]*vis-network[^>]*/?>',
)


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
    Generic widget that renders vis.js-based HTML inside a QWebEngineView.

    Parameters
    ----------
    bg_color : str
        CSS colour string used for the Qt page background and the baseline
        CSS injected into every page (default ``"#1a1a2a"``).
    parent : QWidget | None
    """

    def __init__(self, bg_color: str = "#1a1a2a", parent: QWidget | None = None):
        super().__init__(parent)
        self._bg = bg_color

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_view.setPage(_SilentPage(self.web_view))
        self.web_view.page().setBackgroundColor(QColor(bg_color))
        layout.addWidget(self.web_view)

    # ── public API ────────────────────────────────────────────────────────────

    def set_html(self, raw_html: str, extra_styles: str = "") -> None:
        """
        Patch *raw_html* and load it entirely in-memory.

        Steps
        -----
        1. Replace CDN ``<script>`` / ``<link>`` tags with inlined bundles.
        2. Patch ``<body>`` opening tag with a transparent / bg-colour inline
           style.
        3. Inject a ``<style>`` block before ``</head>`` that sets ``html``,
           ``body``, ``#mynetwork``, ``.vis-network``, and ``canvas`` to fill
           the viewport with *bg_color*.  Any *extra_styles* CSS rules are
           appended inside the same block.
        """
        html = _CDN_SCRIPT_RE.sub(lambda _: _JS_BLOCK,  raw_html)
        html = _CDN_LINK_RE.sub(  lambda _: _CSS_BLOCK, html)

        html = html.replace(
            "<body>",
            f"<body style='margin:0;padding:0;background:{self._bg};"
            f"height:100vh;overflow:hidden'>",
            1,
        )

        base_css = (
            f"  html, body {{ margin:0; padding:0; width:100%; height:100vh;"
            f" background:{self._bg}; overflow:hidden; }}\n"
            f"  #mynetwork {{ width:100% !important; height:100vh !important; }}\n"
            f"  .vis-network {{ background: {self._bg} !important; }}\n"
            f"  canvas {{ background: {self._bg} !important; }}\n"
        )
        extra = (f"  {extra_styles}\n") if extra_styles else ""
        style_block = f"<style>\n{base_css}{extra}</style>\n"

        html = html.replace("</head>", style_block + "</head>", 1)

        self.web_view.setHtml(html)

    @staticmethod
    def net_to_html(net: Network) -> str:
        """
        Convert a pyvis *Network* to an HTML string without writing to disk.

        Uses ``Network.generate_html()`` when available (pyvis ≥ 0.7).
        Falls back to a NamedTemporaryFile that is deleted immediately after
        reading.
        """
        if hasattr(net, "generate_html"):
            return net.generate_html()

        fd, tmp_path = tempfile.mkstemp(suffix=".html")
        os.close(fd)
        try:
            net.save_graph(tmp_path)
            with open(tmp_path, "r", encoding="utf-8") as f:
                return f.read()
        finally:
            os.unlink(tmp_path)

    def run_js(self, js: str) -> None:
        """Run *js* in the currently loaded page."""
        self.web_view.page().runJavaScript(js)
