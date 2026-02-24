from typing import TYPE_CHECKING

from comp382_assignment_2.common.status import Status
from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.content_panel_model import ContentPanelModel
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

        self.model = ContentPanelModel()

        self.connect_signals()
        self.sync_from_current_ui()

    def connect_signals(self):
        self.language_builder.connect_inputs(self.on_dropdown_changed, self.on_input_changed)
        self.right_panel.button_panel.next_btn.clicked.connect(self.on_next_clicked)
        self.right_panel.button_panel.reset_btn.clicked.connect(self.on_reset_clicked)

    def sync_from_current_ui(self):
        self.on_dropdown_changed(-1)
        self.on_input_changed(self.language_builder.input_field.text())

    def on_dropdown_changed(self, _index: int):
        self.model.reg_key = self.language_builder.selected_reg_key()
        self.model.cfl_key = self.language_builder.selected_cfl_key()
        self.model.super_definition = None

        if not self.model.reg_key or not self.model.cfl_key:
            self.model.pda_config_key = None
            self.flow.language_label = ""
            self.right_panel.render_placeholder()
            self.right_panel.set_filtered_input_text("")
            self.right_panel.set_status(Status.IDLE)
            self.flow.render()
            return

        lookup = f"{self.model.reg_key}__{self.model.cfl_key}"
        self.model.pda_config_key = self.app_config.intersection_map.get(lookup)

        labels = getattr(self.app_config, "intersection_labels", {})
        self.flow.language_label = labels.get(self.model.pda_config_key, "") if self.model.pda_config_key else ""

        if not self.model.pda_config_key:
            self.right_panel.render_placeholder()
            self.right_panel.set_filtered_input_text("")
            self.right_panel.set_status(Status.IDLE)
        elif self.model.pda_config_key == "empty":
            self.right_panel.render_empty_language()
            self.right_panel.set_filtered_input_text("")
            self.right_panel.set_status(Status.REJECTED)
        else:
            self.model.super_definition = get_super_pda(self.model.pda_config_key)
            self.right_panel.render_super_pda(self.model.super_definition)
            filtered_text = self.get_filtered_input_text(self.language_builder.input_field.text())
            self.right_panel.set_filtered_input_text(filtered_text)
            self.prepare_super_model(filtered_text)

        self.flow.render()

    def on_input_changed(self, text: str):
        filtered_text = self.get_filtered_input_text(text)
        self.right_panel.set_filtered_input_text(filtered_text)

        if not self.model.reg_key or not self.model.cfl_key or not text:
            self.flow.result_text = ""
            if self.model.super_definition and self.model.pda_config_key not in (None, "empty"):
                self.prepare_super_model(filtered_text)
            else:
                self.right_panel.set_status(Status.IDLE)
            self.flow.render()
            return

        self.flow.result_text = f'"{filtered_text}"' if filtered_text else self.app_config.no_match_text

        if self.model.super_definition and self.model.pda_config_key not in (None, "empty"):
            self.prepare_super_model(filtered_text)

        self.flow.render()

    def on_next_clicked(self):
        if not self.model.super_definition:
            self.right_panel.set_status(Status.IDLE)
            return

        remaining = self.model.super_definition.input_string[self.model.super_definition.input_index:]
        if not remaining:
            if self.model.super_definition.is_accepted():
                self.right_panel.set_status(Status.ACCEPTED)
            else:
                self.right_panel.set_status(Status.REJECTED)
            return

        next_char = remaining[0]
        result = self.model.super_definition.next_step(next_char)
        self.right_panel.super_pda_view.update_state(self.model.super_definition)
        remaining = self.model.super_definition.input_string[self.model.super_definition.input_index:]
        self.right_panel.set_filtered_input_text(remaining)

        if self.model.super_definition.is_accepted():
            self.right_panel.set_status(Status.ACCEPTED)
        elif self.model.super_definition.is_stuck() or not result["transitioned"]:
            self.right_panel.set_status(Status.REJECTED)
        else:
            self.right_panel.set_status(Status.RUNNING)

    def on_reset_clicked(self):
        filtered_text = self.get_filtered_input_text(self.language_builder.input_field.text())

        if not self.model.super_definition:
            self.right_panel.set_status(Status.IDLE)
            self.right_panel.set_filtered_input_text(filtered_text)
            return

        self.model.super_definition.load_input(filtered_text)
        self.right_panel.super_pda_view.reset_state()
        self.right_panel.super_pda_view.update_state(self.model.super_definition)
        self.right_panel.set_filtered_input_text(self.model.super_definition.input_string)
        self.right_panel.set_status(Status.RUNNING if self.model.super_definition.input_string else Status.IDLE)

    def prepare_super_model(self, text: str):
        if not self.model.pda_config_key or self.model.pda_config_key == "empty":
            self.model.super_definition = None
            self.right_panel.set_status(Status.IDLE)
            return

        if not self.model.super_definition:
            self.model.super_definition = get_super_pda(self.model.pda_config_key)
        self.model.super_definition.load_input(text)
        self.right_panel.super_pda_view.reset_state()
        self.right_panel.super_pda_view.update_state(self.model.super_definition)
        self.right_panel.set_status(Status.RUNNING if text else Status.IDLE)

    def find_longest_intersection_substring(self, text: str) -> str:
        if not self.model.reg_key or not self.model.cfl_key:
            return ""

        matcher = _INTERSECTION_LONGEST_MAP.get((self.model.reg_key, self.model.cfl_key))
        if matcher is None:
            return ""

        return matcher(text)

    def get_filtered_input_text(self, text: str) -> str:
        if not text or not self.model.reg_key or not self.model.cfl_key:
            return ""
        if not self.model.pda_config_key or self.model.pda_config_key == "empty":
            return ""
        return self.find_longest_intersection_substring(text)
