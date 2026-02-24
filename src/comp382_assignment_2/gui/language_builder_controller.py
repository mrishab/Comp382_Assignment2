import re

from PySide6.QtCore import QTimer

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.flow_diagram import FlowDiagram
from comp382_assignment_2.gui.language_builder import LangugageBuilder
from comp382_assignment_2.gui.right_content_panel import RightContentPanel
from comp382_assignment_2.pda.pda_loader import load_cfl_pda, load_super_pda, load_super_pda_config
from comp382_assignment_2.gui.pushdown_automata.pushdown_automata_controller import (
    PushdownAutomataController,
)


class LanguageBuilderController:
    """Owns language-selection logic and simulation controls."""

    def __init__(
        self,
        app_config: AppConfig,
        language_builder: LangugageBuilder,
        flow: FlowDiagram,
        right_panel: RightContentPanel,
        pda_view,
        parent=None,
    ):
        self.app_config = app_config
        self.language_builder = language_builder
        self.flow = flow
        self.right_panel = right_panel
        self.pda_view = pda_view

        self._reg_key: str | None = None
        self._cfl_key: str | None = None
        self._pda_config_key: str | None = None
        self._pda_model = None
        self._pda_ctrl: PushdownAutomataController | None = None

        self._sim_timer = QTimer(parent)
        self._sim_timer.setInterval(800)
        self._sim_timer.timeout.connect(self._on_sim_tick)

        self._connect_signals()
        self._update_buttons_enabled()

    def _connect_signals(self):
        self.language_builder.connect_inputs(self._on_dropdown_changed, self._on_input_changed)
        self.right_panel.sim_btn.clicked.connect(self._on_run_simulation)
        self.right_panel.step_btn.clicked.connect(self._on_step)
        self.right_panel.reset_btn.clicked.connect(self._on_reset)

    def _on_dropdown_changed(self, _index: int):
        reg_key = self.language_builder.selected_reg_key()
        cfl_key = self.language_builder.selected_cfl_key()
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

        self._on_input_changed(self.language_builder.input_field.text())
        self._update_buttons_enabled()

    def _on_input_changed(self, text: str):
        self._stop_simulation()

        reg_key = self._reg_key
        cfl_key = self._cfl_key

        if not reg_key or not cfl_key or not text:
            self.flow.dfa_status = None
            self.flow.pda_status = None
            self.flow.result_text = ""
            self.flow.gate_status = "∩ Gate"
            self.flow.update()
            self._update_status(self.app_config.status_idle)
            self._update_buttons_enabled()
            return

        dfa_pattern = self.app_config.regular_languages.get(reg_key, {}).get("regex", "")
        dfa_accept = bool(re.match(dfa_pattern, text)) if dfa_pattern else False
        self.flow.dfa_status = dfa_accept

        cfl_accept = self._test_cfl_acceptance(cfl_key, text)
        self.flow.pda_status = cfl_accept

        super_accept = self._test_super_pda_acceptance(text)

        if super_accept:
            self.flow.gate_status = "✓ Match"
            self.flow.result_text = f'"{text}"'
        else:
            self.flow.gate_status = "✗ No Match"
            self.flow.result_text = self.app_config.no_match_text

        self.flow.update()
        self._update_status(self.app_config.status_idle)
        self._update_buttons_enabled()

    def _on_run_simulation(self):
        if not self._pda_ctrl or not self._pda_model:
            return

        self._pda_ctrl.load_input(self.language_builder.input_field.text())

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

        current_text = self.language_builder.input_field.text()
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
            self._pda_ctrl.load_input(self.language_builder.input_field.text())
        self._update_status(self.app_config.status_idle)
        self._update_buttons_enabled()

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

        labels = getattr(self.app_config, "intersection_labels", {})
        lang_label = labels.get(pda_config_key, pda_config_key)
        self._update_lang_display(lang_label)

        if pda_config_key == "empty":
            self._pda_model = None
            self._pda_ctrl = None
            self._set_view_mode("empty")
            return

        self._set_view_mode("pda")
        self._pda_model = load_super_pda(pda_config_key)
        pda_config = load_super_pda_config(pda_config_key)
        self._pda_ctrl = PushdownAutomataController(self._pda_model, self.pda_view, pda_config)

    def _update_lang_display(self, label: str):
        self.flow.language_label = label
        self.flow.update()
        self.right_panel.set_lang_label(label)

    def _set_view_mode(self, mode: str):
        self.right_panel.set_mode(mode)

    def _test_cfl_acceptance(self, cfl_key: str, text: str) -> bool:
        try:
            model = load_cfl_pda(cfl_key)
            model.load_input(text)
            while not model.is_stuck() and not model.is_accepted():
                model.step()
            return model.is_accepted()
        except KeyError:
            return False

    def _test_super_pda_acceptance(self, text: str) -> bool:
        if not self._pda_config_key or self._pda_config_key == "empty":
            return False
        try:
            model = load_super_pda(self._pda_config_key)
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
        has_ctrl = self._pda_ctrl is not None
        has_model = self._pda_model is not None
        has_input = bool(self.language_builder.input_field.text())
        sim_running = self._sim_timer.isActive()
        is_empty_lang = self._pda_config_key == "empty"

        can_run = has_ctrl and has_model and has_input and not sim_running and not is_empty_lang
        finished = has_model and (self._pda_model.is_accepted() or self._pda_model.is_stuck())

        self.right_panel.set_buttons_enabled(
            sim=can_run,
            step=can_run and not finished,
            reset=has_ctrl and has_input and not is_empty_lang,
        )
