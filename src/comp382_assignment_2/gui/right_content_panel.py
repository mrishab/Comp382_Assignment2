from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.pushdown_automata.pushdown_automata_view import (
    PushdownAutomataView,
)

_BTN_STYLE = (
    "QPushButton { background:#495057; color:white; border:1px solid #6c757d; "
    "border-radius:5px; font-size:13px; font-weight:bold; padding: 0 12px; }"
    "QPushButton:hover { background:#6c757d; }"
    "QPushButton:pressed { background:#343a40; }"
    "QPushButton:disabled { background:#333; color:#666; border-color:#444; }"
)


class RightContentPanel(QWidget):
    """Right panel: Super PDA visualisation + simulation controls."""

    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("PdaContainer")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # -- Header row -------------------------------------------------------
        header_row = QHBoxLayout()

        title = QLabel(self.app_config.super_pda_label)
        title.setStyleSheet("color: #ddd; font-size: 14px; font-weight: bold;")
        header_row.addWidget(title)

        # Intersection language badge (shows e.g. "aⁿbⁿ")
        self.lang_badge = QLabel("")
        self.lang_badge.setStyleSheet(
            "color: #80c0ff; font-size: 13px; font-weight: bold; "
            "padding: 2px 10px; border: 1px solid #4A90D9; border-radius: 3px; "
            "background: #1e2a3e;"
        )
        self.lang_badge.setVisible(False)
        header_row.addWidget(self.lang_badge)

        header_row.addStretch()

        self.status_label = QLabel(self.app_config.status_idle)
        self.status_label.setStyleSheet(
            "color: #888; font-size: 12px; padding: 2px 8px; "
            "border: 1px solid #444; border-radius: 3px;"
        )
        header_row.addWidget(self.status_label)
        layout.addLayout(header_row)

        # -- Placeholder (shown until both dropdowns are selected) ------------
        self.placeholder_label = QLabel(
            "Select a Regular Language and a CFL\nto construct the Super PDA"
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet(
            "color: #888; font-size: 16px; font-style: italic; "
            "background: #1a1a2a; border: 2px dashed #444; "
            "border-radius: 10px; padding: 40px;"
        )
        layout.addWidget(self.placeholder_label, stretch=1)

        # -- PDA PyVis view (hidden until a valid PDA is loaded) --------------
        self.pda_view = PushdownAutomataView()
        self.pda_view.setVisible(False)
        layout.addWidget(self.pda_view, stretch=1)

        # -- Empty language overlay (hidden by default) -----------------------
        self.empty_label = QLabel(self.app_config.empty_language_message)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(
            "color: #E74C3C; font-size: 18px; font-weight: bold; "
            "background: #1a1a2a; border: 2px dashed #E74C3C; "
            "border-radius: 10px; padding: 40px;"
        )
        self.empty_label.setVisible(False)
        layout.addWidget(self.empty_label, stretch=1)

        # -- Control buttons --------------------------------------------------
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sim_btn = QPushButton(self.app_config.run_simulation_btn)
        self.step_btn = QPushButton(self.app_config.step_btn)
        self.reset_btn = QPushButton(self.app_config.reset_btn)

        for btn in (self.sim_btn, self.step_btn, self.reset_btn):
            btn.setFixedHeight(34)
            btn.setMinimumWidth(100)
            btn.setStyleSheet(_BTN_STYLE)
            btn_row.addWidget(btn)

        layout.addLayout(btn_row)
