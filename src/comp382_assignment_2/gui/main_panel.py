import re
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QSplitter,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.header import Header
from comp382_assignment_2.gui.utils import load_stylesheet
from comp382_assignment_2.gui.flow_diagram import FlowDiagram
from comp382_assignment_2.gui.validated_line_edit import ValidatedLineEdit
from comp382_assignment_2.gui.virtual_keyboard import VirtualKeyboard
from comp382_assignment_2.common.symbols import STRING_SYMBOLS
from comp382_assignment_2.pda.pda_loader import load_pda
from comp382_assignment_2.gui.content_panel import ContentPanel
from comp382_assignment_2.gui.pushdown_automata.pushdown_automata_view import (
    PushdownAutomataView,
)
from comp382_assignment_2.gui.pushdown_automata.pushdown_automata_controller import (
    PushdownAutomataController,
)


_DFA_PATTERNS = {
    "a_star_b_star": r"^a*b*$",
    "a_b_star_a": r"^ab*a$",
    "a_star": r"^a*$",
}

_BTN_STYLE = (
    "QPushButton { background:#495057; color:white; border:1px solid #6c757d; "
    "border-radius:5px; font-size:13px; font-weight:bold; padding: 0 12px; }"
    "QPushButton:hover { background:#6c757d; }"
    "QPushButton:pressed { background:#343a40; }"
    "QPushButton:disabled { background:#333; color:#666; border-color:#444; }"
)


class MainPanel(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config

        self._reg_key: str | None = None
        self._cfl_key: str | None = None
        self._pda_config_key: str | None = None  # current intersection PDA key
        self._pda_model = None
        self._pda_ctrl: PushdownAutomataController | None = None

        self._sim_timer = QTimer(self)
        self._sim_timer.setInterval(800)
        self._sim_timer.timeout.connect(self._on_sim_tick)

        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(load_stylesheet("main_panel.css"))
        self.setObjectName("MainPanel")

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 10)
        root.setSpacing(6)

        # Header (spans full width)
        root.addWidget(Header(self.app_config))

        # Horizontal splitter: LEFT | RIGHT
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        splitter.setChildrenCollapsible(False)

        # Left panel: language selectors + input + flow diagram
        content = ContentPanel(self.app_config)
        splitter.addWidget(content)
        splitter.addWidget(self._build_right_panel())

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter, stretch=1)

        # Grab widget refs from sub-components for signal wiring
        self.reg_dropdown = content.language_builder.reg_dd
        self.cfl_dropdown = content.language_builder.cfl_dd
        self.input_field = content.language_builder.input_bar.input_field
        self.keyboard = content.language_builder.input_bar.keyboard
        self.flow = content.flow

        # Wire signals
        self.reg_dropdown.currentIndexChanged.connect(self._on_dropdown_changed)
        self.cfl_dropdown.currentIndexChanged.connect(self._on_dropdown_changed)
        self.input_field.textChanged.connect(self._on_input_changed)
        self.sim_btn.clicked.connect(self._on_run_simulation)
        self.step_btn.clicked.connect(self._on_step)
        self.reset_btn.clicked.connect(self._on_reset)

        self._update_buttons_enabled()

    # ── left panel ───────────────────────────────────────────────────────

    def _build_left_panel(self) -> QFrame:

        # -- Virtual keyboard -------------------------------------------------
        self.keyboard = VirtualKeyboard(STRING_SYMBOLS, self.input_field)
        layout.addWidget(self.keyboard)

        # -- Flow diagram (fills remaining space) -----------------------------
        self.flow = FlowDiagram()
        self.flow.setMinimumHeight(160)
        layout.addWidget(self.flow, stretch=1)

        return panel

    # ── right panel ──────────────────────────────────────────────────────

    def _build_right_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("PdaContainer")
        layout = QVBoxLayout(panel)
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

        return panel

    # ── slot handlers ────────────────────────────────────────────────────

    def _on_dropdown_changed(self, _index: int):
        reg_key = self.reg_dropdown.currentData()
        cfl_key = self.cfl_dropdown.currentData()
        self._reg_key = reg_key
        self._cfl_key = cfl_key

        self._stop_simulation()

        if reg_key and cfl_key:
            self._load_super_pda(reg_key, cfl_key)
        else:
            self._pda_model = None
            self._pda_ctrl = None
            self._pda_config_key = None
            self._update_lang_display("")
            self._set_view_mode("placeholder")

        self._on_input_changed(self.input_field.text())
        self._update_buttons_enabled()

    def _on_input_changed(self, text: str):
        self._stop_simulation()

        reg_key = self._reg_key
        cfl_key = self._cfl_key

        if not reg_key or not cfl_key or not text:
            self.flow.dfa_status = None
            self.flow.pda_status = None
            self.flow.result_text = ""
            self.flow.gate_status = "\u2229 Gate"
            self.flow.update()
            self._update_status(self.app_config.status_idle)
            self._update_buttons_enabled()
            return

        # DFA check (visual feedback only)
        dfa_pattern = _DFA_PATTERNS.get(reg_key, "")
        dfa_accept = bool(re.match(dfa_pattern, text)) if dfa_pattern else False
        self.flow.dfa_status = dfa_accept

        # CFL PDA check (visual feedback only)
        cfl_accept = self._test_cfl_acceptance(cfl_key, text)
        self.flow.pda_status = cfl_accept

        # The actual acceptance is determined by the super PDA (intersection).
        super_accept = self._test_super_pda_acceptance(text)

        if super_accept:
            self.flow.gate_status = "\u2713 Match"
            self.flow.result_text = f'"{text}"'
        else:
            self.flow.gate_status = "\u2717 No Match"
            self.flow.result_text = self.app_config.no_match_text

        self.flow.update()
        self._update_status(self.app_config.status_idle)
        self._update_buttons_enabled()

    def _on_run_simulation(self):
        if not self._pda_ctrl or not self._pda_model:
            return
        # Load current input text into the PDA model (resets it)
        self._pda_ctrl.load_input(self.input_field.text())

        self._update_status(self.app_config.status_running)
        self._sim_timer.start()
        self._update_buttons_enabled()

    def _on_sim_tick(self):
        if not self._pda_ctrl or not self._pda_model:
            self._stop_simulation()
            return
        if self._pda_model.is_accepted():
            self._stop_simulation()
            self._update_status(self.app_config.status_accepted)
            return
        if self._pda_model.is_stuck():
            self._stop_simulation()
            self._update_status(self.app_config.status_rejected)
            return
        self._pda_ctrl.step()

    def _on_step(self):
        if not self._pda_ctrl or not self._pda_model:
            return
        # If no input loaded yet (first step), load the current text
        current_text = self.input_field.text()
        if self._pda_model.input_string != current_text:
            self._pda_ctrl.load_input(current_text)
        self._pda_ctrl.step()
        if self._pda_model.is_accepted():
            self._update_status(self.app_config.status_accepted)
        elif self._pda_model.is_stuck():
            self._update_status(self.app_config.status_rejected)
        else:
            self._update_status(self.app_config.status_running)
        self._update_buttons_enabled()

    def _on_reset(self):
        self._stop_simulation()
        if self._pda_ctrl:
            self._pda_ctrl.load_input(self.input_field.text())
        self._update_status(self.app_config.status_idle)
        self._update_buttons_enabled()

    # ── internal helpers ─────────────────────────────────────────────────

    def _load_super_pda(self, reg_key: str, cfl_key: str):
        lookup = f"{reg_key}__{cfl_key}"
        pda_config_key = self.app_config.intersection_map.get(lookup)
        self._pda_config_key = pda_config_key

        if not pda_config_key:
            self._pda_model = None
            self._pda_ctrl = None
            self._update_lang_display("")
            self._set_view_mode("placeholder")
            return

        # Resolve the display label for this intersection
        labels = getattr(self.app_config, "intersection_labels", {})
        lang_label = labels.get(pda_config_key, pda_config_key)
        self._update_lang_display(lang_label)

        if pda_config_key == "empty":
            # Empty language — no PDA to simulate
            self._pda_model = None
            self._pda_ctrl = None
            self._set_view_mode("empty")
            return

        self._set_view_mode("pda")
        self._pda_model = load_pda(pda_config_key)
        self._pda_ctrl = PushdownAutomataController(self._pda_model, self.pda_view)

    def _update_lang_display(self, label: str):
        """Update the language label in both the flow diagram and right panel badge."""
        self.flow.language_label = label
        self.flow.update()

        if label:
            self.lang_badge.setText(f"L = {label}")
            self.lang_badge.setVisible(True)
        else:
            self.lang_badge.setVisible(False)

    def _set_view_mode(self, mode: str):
        """Switch the right panel between 'placeholder', 'empty', and 'pda'."""
        self.placeholder_label.setVisible(mode == "placeholder")
        self.empty_label.setVisible(mode == "empty")
        self.pda_view.setVisible(mode == "pda")

    def _test_cfl_acceptance(self, cfl_key: str, text: str) -> bool:
        """Test if text is accepted by the raw CFL PDA (for visual feedback)."""
        try:
            model = load_pda(cfl_key)
            model.load_input(text)
            while not model.is_stuck() and not model.is_accepted():
                model.step()
            return model.is_accepted()
        except KeyError:
            return False

    def _test_super_pda_acceptance(self, text: str) -> bool:
        """Test if text is accepted by the super PDA (the intersection language)."""
        if not self._pda_config_key or self._pda_config_key == "empty":
            return False
        try:
            model = load_pda(self._pda_config_key)
            model.load_input(text)
            while not model.is_stuck() and not model.is_accepted():
                model.step()
            return model.is_accepted()
        except KeyError:
            return False

    def _stop_simulation(self):
        self._sim_timer.stop()

    def _update_status(self, text: str):
        self.status_label.setText(text)
        color_map = {
            self.app_config.status_accepted: "#5CB85C",
            self.app_config.status_rejected: "#E74C3C",
            self.app_config.status_running: "#FFD700",
        }
        color = color_map.get(text, "#888")
        self.status_label.setStyleSheet(
            f"color: {color}; font-size: 12px; padding: 2px 8px; "
            f"border: 1px solid {color}; border-radius: 3px;"
        )

    def _update_buttons_enabled(self):
        has_ctrl = self._pda_ctrl is not None
        has_model = self._pda_model is not None
        has_input = bool(self.input_field.text())
        sim_running = self._sim_timer.isActive()
        is_empty_lang = self._pda_config_key == "empty"

        can_run = (
            has_ctrl
            and has_model
            and has_input
            and not sim_running
            and not is_empty_lang
        )
        finished = (
            has_model and (self._pda_model.is_accepted() or self._pda_model.is_stuck())
            if has_model
            else False
        )

        self.sim_btn.setEnabled(can_run)
        self.step_btn.setEnabled(can_run and not finished)
        self.reset_btn.setEnabled(has_ctrl and has_input and not is_empty_lang)
