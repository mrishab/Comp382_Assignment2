import re
from typing import TYPE_CHECKING

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.pda.pda_loader import load_cfl_pda, load_super_pda, load_super_pda_config

if TYPE_CHECKING:
    from comp382_assignment_2.gui.content_panel import ContentPanel


class ContentPanelController:
    """Logic layer that connects left selections/input with flow + right Super PDA view."""

    def __init__(self, app_config: AppConfig, content_panel: "ContentPanel"):
        self.app_config = app_config
        self.content_panel = content_panel

        self.language_builder = self.content_panel.left.language_builder
        self.flow = self.content_panel.left.flow
        self.right_panel = self.content_panel.right

        self._reg_key: str | None = None
        self._cfl_key: str | None = None
        self._pda_config_key: str | None = None

        self._connect_signals()
        self._sync_from_current_ui()

    def _connect_signals(self):
        self.language_builder.connect_inputs(self._on_dropdown_changed, self._on_input_changed)

    def _sync_from_current_ui(self):
        self._on_dropdown_changed(-1)
        self._on_input_changed(self.language_builder.input_field.text())

    def _on_dropdown_changed(self, _index: int):
        self._reg_key = self.language_builder.selected_reg_key()
        self._cfl_key = self.language_builder.selected_cfl_key()

        if not self._reg_key or not self._cfl_key:
            self._pda_config_key = None
            self.flow.language_label = ""
            self.right_panel.render_placeholder()
            self.flow.update()
            return

        lookup = f"{self._reg_key}__{self._cfl_key}"
        self._pda_config_key = self.app_config.intersection_map.get(lookup)

        labels = getattr(self.app_config, "intersection_labels", {})
        self.flow.language_label = labels.get(self._pda_config_key, "") if self._pda_config_key else ""

        if not self._pda_config_key:
            self.right_panel.render_placeholder()
        elif self._pda_config_key == "empty":
            self.right_panel.render_empty_language()
        else:
            pda_config = load_super_pda_config(self._pda_config_key)
            self.right_panel.render_super_pda(pda_config)

        self.flow.update()

    def _on_input_changed(self, text: str):
        if not self._reg_key or not self._cfl_key or not text:
            self.flow.dfa_status = None
            self.flow.pda_status = None
            self.flow.result_text = ""
            self.flow.gate_status = "∩ Gate"
            self.flow.update()
            return

        dfa_pattern = self.app_config.regular_languages.get(self._reg_key, {}).get("regex", "")
        dfa_accept = bool(re.match(dfa_pattern, text)) if dfa_pattern else False
        self.flow.dfa_status = dfa_accept

        cfl_accept = self._test_cfl_acceptance(self._cfl_key, text)
        self.flow.pda_status = cfl_accept

        super_accept = self._test_super_pda_acceptance(text)
        if super_accept:
            self.flow.gate_status = "✓ Match"
            self.flow.result_text = f'"{text}"'
        else:
            self.flow.gate_status = "✗ No Match"
            self.flow.result_text = self.app_config.no_match_text

        self.flow.update()

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
