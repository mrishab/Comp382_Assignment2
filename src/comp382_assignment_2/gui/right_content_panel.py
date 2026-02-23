"""
right_content_panel.py - Super PDA state-machine graph + Stack graph + simulation controls.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSplitter,
)
from PySide6.QtCore import Qt

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.super_pda_graph import SuperPDAGraph
from comp382_assignment_2.gui.stack_graph import StackGraph

_BTN_STYLE = (
    "QPushButton { background:#495057; color:white; border:1px solid #6c757d; "
    "border-radius:5px; font-size:13px; font-weight:bold; padding: 0 12px; }"
    "QPushButton:hover { background:#6c757d; }"
    "QPushButton:pressed { background:#343a40; }"
    "QPushButton:disabled { background:#333; color:#666; border-color:#444; }"
)


class _CombinedView:
    """
    Proxy that drives both the PDA state-machine graph and the stack graph from
    a single render_graph / update_state interface (matches PushdownAutomataController expectations).
    """
    def __init__(self, pda_graph: SuperPDAGraph, stack_graph: StackGraph):
        self._pda   = pda_graph
        self._stack = stack_graph

    def render_graph(self, config: dict):
        self._pda.render_graph(config)

    def update_state(self, model):
        self._pda.update_state(model)
        self._stack.update_stack(model.stack)

    # Back-compat
    def update_view(self, model):
        self.update_state(model)


class RightContentPanel(QWidget):
    """Right panel: Super PDA graph | Stack graph + simulation controls."""

    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("PdaContainer")
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        # ── Header row ────────────────────────────────────────────────────────
        header = QHBoxLayout()

        title = QLabel(self.app_config.super_pda_label)
        title.setStyleSheet("color:#ddd; font-size:14px; font-weight:bold;")
        header.addWidget(title)

        self.lang_badge = QLabel("")
        self.lang_badge.setStyleSheet(
            "color:#80c0ff; font-size:13px; font-weight:bold; "
            "padding:2px 10px; border:1px solid #4A90D9; border-radius:3px; "
            "background:#1e2a3e;"
        )
        self.lang_badge.setVisible(False)
        header.addWidget(self.lang_badge)

        header.addStretch()

        self.status_label = QLabel(self.app_config.status_idle)
        self.status_label.setStyleSheet(
            "color:#888; font-size:12px; padding:2px 8px; "
            "border:1px solid #444; border-radius:3px;"
        )
        header.addWidget(self.status_label)

        root.addLayout(header)

        # ── Main area: PDA graph (left) | Stack graph (right) ─────────────────
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setStyleSheet("QSplitter::handle { background: #333; }")

        # PDA state-machine graph
        self.pda_graph = SuperPDAGraph()
        self._splitter.addWidget(self.pda_graph)

        # Stack visualisation
        self.stack_graph = StackGraph()
        self._splitter.addWidget(self.stack_graph)

        self._splitter.setSizes([680, 220])          # ~75% / ~25% split
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, False)
        root.addWidget(self._splitter, stretch=1)

        # Combined view proxy (drives both graphs via controller)
        self.pda_view = _CombinedView(self.pda_graph, self.stack_graph)

        # ── Placeholder overlay (shown when no PDA is loaded) ─────────────────
        self.placeholder_label = QLabel(
            "Select a Regular Language and a CFL\nto construct the Super PDA"
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet(
            "color:#888; font-size:16px; font-style:italic; "
            "background:#1a1a2a; border:2px dashed #444; "
            "border-radius:10px; padding:40px;"
        )
        self.placeholder_label.setVisible(False)
        root.addWidget(self.placeholder_label, stretch=1)

        # ── Empty-language overlay ─────────────────────────────────────────────
        self.empty_label = QLabel(self.app_config.empty_language_message)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color:#E74C3C; font-size:18px; font-weight:bold; "
            "background:#1a1a2a; border:2px dashed #E74C3C; "
            "border-radius:10px; padding:40px;"
        )
        self.empty_label.setVisible(False)
        root.addWidget(self.empty_label, stretch=1)

        # ── Control buttons ────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sim_btn   = QPushButton(self.app_config.run_simulation_btn)
        self.step_btn  = QPushButton(self.app_config.step_btn)
        self.reset_btn = QPushButton(self.app_config.reset_btn)

        for btn in (self.sim_btn, self.step_btn, self.reset_btn):
            btn.setFixedHeight(34)
            btn.setMinimumWidth(100)
            btn.setStyleSheet(_BTN_STYLE)
            btn_row.addWidget(btn)

        root.addLayout(btn_row)

        # Start in pda mode so both graphs are visible immediately
        self._set_mode("pda")

    # ── public slot for main_panel to switch modes ─────────────────────────────

    def set_mode(self, mode: str):
        """mode: 'placeholder' | 'empty' | 'pda'"""
        self._set_mode(mode)

    def _set_mode(self, mode: str):
        self._splitter.setVisible(mode == "pda")
        self.placeholder_label.setVisible(mode == "placeholder")
        self.empty_label.setVisible(mode == "empty")

    # ── right-panel display API (called by MainPanel) ──────────────────────────

    def set_status(self, text: str):
        """Update the status badge text and colour."""
        cfg = self.app_config
        _COLOURS = {
            cfg.status_accepted: "#5CB85C",
            cfg.status_rejected: "#E74C3C",
            cfg.status_running:  "#FFD700",
        }
        colour = _COLOURS.get(text, "#888")
        self.status_label.setText(text)
        self.status_label.setStyleSheet(
            f"color:{colour};font-size:12px;padding:2px 8px;"
            f"border:1px solid {colour};border-radius:3px;"
        )

    def set_lang_label(self, label: str):
        """Show or hide the intersection-language badge."""
        if label:
            self.lang_badge.setText(f"L = {label}")
            self.lang_badge.setVisible(True)
        else:
            self.lang_badge.setVisible(False)

    def set_buttons_enabled(self, *, sim: bool, step: bool, reset: bool):
        """Enable/disable the simulation control buttons."""
        self.sim_btn.setEnabled(sim)
        self.step_btn.setEnabled(step)
        self.reset_btn.setEnabled(reset)
