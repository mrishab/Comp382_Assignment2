import re
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QTimer

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.header import Header
from comp382_assignment_2.gui.utils import load_stylesheet
from comp382_assignment_2.pda.pda_loader import load_pda
from comp382_assignment_2.gui.content_panel import ContentPanel
from comp382_assignment_2.gui.pushdown_automata.pushdown_automata_controller import (
    PushdownAutomataController,
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

        # Content area: left | right horizontal layout
        content = ContentPanel(self.app_config)
        root.addWidget(content, stretch=1)

        # Aliases from left panel
        self.reg_dropdown = content.left.language_builder.reg_dd
        self.cfl_dropdown = content.left.language_builder.cfl_dd
        self.input_field = content.left.language_builder.input_bar.input_field
        self.keyboard = content.left.language_builder.input_bar.keyboard
        self.flow = content.left.flow

        # Right panel — interact through its public API only
        self.right_panel = content.right
        self.pda_view = content.right.pda_view   # _CombinedView (drives graph + stack)

        # Wire signals
        self.reg_dropdown.currentIndexChanged.connect(self._on_dropdown_changed)
        self.cfl_dropdown.currentIndexChanged.connect(self._on_dropdown_changed)
        self.input_field.textChanged.connect(self._on_input_changed)
        content.right.sim_btn.clicked.connect(self._on_run_simulation)
        content.right.step_btn.clicked.connect(self._on_step)
        content.right.reset_btn.clicked.connect(self._on_reset)

        self._update_buttons_enabled()

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
        dfa_pattern = self.app_config.regular_languages.get(reg_key, {}).get("regex", "")
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
        self.right_panel.set_lang_label(label)

    def _set_view_mode(self, mode: str):
        """Switch the right panel between 'placeholder', 'empty', and 'pda'."""
        self.right_panel.set_mode(mode)

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
        self.right_panel.set_status(text)

    def _update_buttons_enabled(self):
        has_ctrl      = self._pda_ctrl is not None
        has_model     = self._pda_model is not None
        has_input     = bool(self.input_field.text())
        sim_running   = self._sim_timer.isActive()
        is_empty_lang = self._pda_config_key == "empty"

        can_run  = has_ctrl and has_model and has_input and not sim_running and not is_empty_lang
        finished = has_model and (self._pda_model.is_accepted() or self._pda_model.is_stuck())

        self.right_panel.set_buttons_enabled(
            sim=can_run,
            step=can_run and not finished,
            reset=has_ctrl and has_input and not is_empty_lang,
        )
