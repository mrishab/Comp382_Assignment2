from typing import TYPE_CHECKING

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.matchers.intersection_matchers import (
    intersect_r1_c1,
    intersect_r1_c2,
    intersect_r1_c3,
    intersect_r2_c1,
    intersect_r2_c2,
    intersect_r2_c3,
    intersect_r3_c1,
    intersect_r3_c2,
    intersect_r3_c3,
)
from comp382_assignment_2.super_pda.base import BaseSuperPDA
from comp382_assignment_2.super_pda.registry import get_super_pda

if TYPE_CHECKING:
    from comp382_assignment_2.gui.content_panel import ContentPanel


_INTERSECTION_LONGEST_MAP = {
    ("a_star_b_star", "an_bn"): intersect_r1_c1,
    ("a_star_b_star", "a_bn_a"): intersect_r1_c2,
    ("a_star_b_star", "bn"): intersect_r1_c3,
    ("a_b_star_a", "an_bn"): intersect_r2_c1,
    ("a_b_star_a", "a_bn_a"): intersect_r2_c2,
    ("a_b_star_a", "bn"): intersect_r2_c3,
    ("a_star", "an_bn"): intersect_r3_c1,
    ("a_star", "a_bn_a"): intersect_r3_c2,
    ("a_star", "bn"): intersect_r3_c3,
}


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
        self._super_definition: BaseSuperPDA | None = None

        self._connect_signals()
        self._sync_from_current_ui()

    def _connect_signals(self):
        self.language_builder.connect_inputs(self._on_dropdown_changed, self._on_input_changed)
        self.right_panel.button_panel.next_btn.clicked.connect(self._on_next_clicked)
        self.right_panel.button_panel.reset_btn.clicked.connect(self._on_reset_clicked)

    def _sync_from_current_ui(self):
        self._on_dropdown_changed(-1)
        self._on_input_changed(self.language_builder.input_field.text())

    def _on_dropdown_changed(self, _index: int):
        self._reg_key = self.language_builder.selected_reg_key()
        self._cfl_key = self.language_builder.selected_cfl_key()
        self._super_definition = None

        if not self._reg_key or not self._cfl_key:
            self._pda_config_key = None
            self.flow.language_label = ""
            self.right_panel.render_placeholder()
            self.right_panel.set_filtered_input_text("")
            self.right_panel.set_status("--")
            self.flow.update()
            return

        lookup = f"{self._reg_key}__{self._cfl_key}"
        self._pda_config_key = self.app_config.intersection_map.get(lookup)

        labels = getattr(self.app_config, "intersection_labels", {})
        self.flow.language_label = labels.get(self._pda_config_key, "") if self._pda_config_key else ""

        if not self._pda_config_key:
            self.right_panel.render_placeholder()
            self.right_panel.set_filtered_input_text("")
            self.right_panel.set_status("--")
        elif self._pda_config_key == "empty":
            self.right_panel.render_empty_language()
            self.right_panel.set_filtered_input_text("")
            self.right_panel.set_status("rejected")
        else:
            self._super_definition = get_super_pda(self._pda_config_key)
            self.right_panel.render_super_pda(self._super_definition)
            self._prepare_super_model(self.language_builder.input_field.text())

        self.flow.update()

    def _on_input_changed(self, text: str):
        self.right_panel.set_filtered_input_text(text)

        if not self._reg_key or not self._cfl_key or not text:
            self.flow.result_text = ""
            self.flow.gate_status = "∩ Gate"
            if self._super_definition and self._pda_config_key not in (None, "empty"):
                self._prepare_super_model(text)
            else:
                self.right_panel.set_status("--")
            self.flow.update()
            return

        longest = self._find_longest_intersection_substring(text)
        self.flow.gate_status = "Longest ∩"
        self.flow.result_text = f'"{longest}"' if longest else self.app_config.no_match_text

        if self._super_definition and self._pda_config_key not in (None, "empty"):
            self._prepare_super_model(text)

        self.flow.update()

    def _on_next_clicked(self):
        if not self._super_definition:
            self.right_panel.set_status("--")
            return

        remaining = self._super_definition.input_string[self._super_definition.input_index:]
        if not remaining:
            if self._super_definition.is_accepted():
                self.right_panel.set_status("accepted")
            else:
                self.right_panel.set_status("rejected")
            return

        next_char = remaining[0]
        result = self._super_definition.next_step(next_char)
        self.right_panel.super_pda_view.update_state(self._super_definition)
        remaining = self._super_definition.input_string[self._super_definition.input_index:]
        self.right_panel.set_filtered_input_text(remaining)

        if self._super_definition.is_accepted():
            self.right_panel.set_status("accepted")
        elif self._super_definition.is_stuck() or not result["transitioned"]:
            self.right_panel.set_status("rejected")
        else:
            self.right_panel.set_status("running")

    def _on_reset_clicked(self):
        if not self._super_definition:
            self.right_panel.set_status("--")
            self.right_panel.set_filtered_input_text(self.language_builder.input_field.text())
            return

        self._super_definition.load_input(self.language_builder.input_field.text())
        self.right_panel.super_pda_view.reset_state()
        self.right_panel.super_pda_view.update_state(self._super_definition)
        self.right_panel.set_filtered_input_text(self._super_definition.input_string)
        self.right_panel.set_status("running" if self._super_definition.input_string else "--")

    def _prepare_super_model(self, text: str):
        if not self._pda_config_key or self._pda_config_key == "empty":
            self._super_definition = None
            self.right_panel.set_status("--")
            return

        if not self._super_definition:
            self._super_definition = get_super_pda(self._pda_config_key)
        self._super_definition.load_input(text)
        self.right_panel.super_pda_view.reset_state()
        self.right_panel.super_pda_view.update_state(self._super_definition)
        self.right_panel.set_status("running" if text else "--")

    def _find_longest_intersection_substring(self, text: str) -> str:
        if not self._reg_key or not self._cfl_key:
            return ""

        matcher = _INTERSECTION_LONGEST_MAP.get((self._reg_key, self._cfl_key))
        if matcher is None:
            return ""

        return matcher(text)
