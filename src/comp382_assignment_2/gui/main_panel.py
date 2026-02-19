from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel
)
from PySide6.QtCore import Qt

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.header import Header
from comp382_assignment_2.gui.utils import load_stylesheet
from comp382_assignment_2.gui.pushdown_automata.pushdown_automata_view import PushdownAutomataView
from comp382_assignment_2.gui.pushdown_automata.pushdown_automata_controller import PushdownAutomataController
from comp382_assignment_2.pda.example_pda import create_an_bn_pda


class MainPanel(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(load_stylesheet('main_panel.css'))
        self.setObjectName("MainPanel")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 16)
        root.setSpacing(12)

        # ── Header ──────────────────────────────────────────────────────────
        root.addWidget(Header(self.app_config))

        # ── Input row ───────────────────────────────────────────────────────
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Input:"))

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("e.g. aabb  (language: aⁿbⁿ)")
        input_row.addWidget(self.input_field, stretch=1)

        self.load_btn = QPushButton("Load")
        self.load_btn.setFixedWidth(72)
        input_row.addWidget(self.load_btn)
        root.addLayout(input_row)

        # ── PDA graph view ───────────────────────────────────────────────────
        model = create_an_bn_pda()
        self.pda_view = PushdownAutomataView()
        self.pda_ctrl = PushdownAutomataController(model, self.pda_view)
        root.addWidget(self.pda_view, stretch=1)

        # ── Control buttons row ─────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.step_btn    = QPushButton("⏭ Step")
        self.reset_btn   = QPushButton("↺ Reset")
        self.run_btn     = QPushButton("▶ Run All")

        for btn in (self.step_btn, self.reset_btn, self.run_btn):
            btn.setFixedHeight(36)
            btn_row.addWidget(btn)

        root.addLayout(btn_row)

        # ── Wire signals ────────────────────────────────────────────────────
        self.load_btn.clicked.connect(self._on_load)
        self.input_field.returnPressed.connect(self._on_load)
        self.step_btn.clicked.connect(self.pda_ctrl.step)
        self.reset_btn.clicked.connect(self.pda_ctrl.reset)
        self.run_btn.clicked.connect(self.pda_ctrl.run_to_end)

    def _on_load(self):
        self.pda_ctrl.load_input(self.input_field.text().strip())
