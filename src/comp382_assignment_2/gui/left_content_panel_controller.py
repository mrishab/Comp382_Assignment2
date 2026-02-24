from comp382_assignment_2.gui.flow_diagram import FlowDiagram
from comp382_assignment_2.gui.language_builder import LangugageBuilder


class LeftContentPanelController:
    """Connect LanguageBuilder selections/input to FlowDiagram labels."""

    def __init__(self, language_builder: LangugageBuilder, flow: FlowDiagram):
        self.language_builder = language_builder
        self.flow = flow

        self.language_builder.reg_dd.currentIndexChanged.connect(self.on_selection_changed)
        self.language_builder.cfl_dd.currentIndexChanged.connect(self.on_selection_changed)
        self.language_builder.input_field.textChanged.connect(self.on_input_changed)

        self.sync_flow_labels()

    def sync_flow_labels(self):
        self.flow.selected_regex = self.language_builder.selected_reg_label()
        self.flow.selected_cfl = self.language_builder.selected_cfl_label()
        self.flow.input_value = self.language_builder.input_field.text()
        self.flow.render()

    def on_selection_changed(self, _index: int):
        self.flow.selected_regex = self.language_builder.selected_reg_label()
        self.flow.selected_cfl = self.language_builder.selected_cfl_label()
        self.flow.render()

    def on_input_changed(self, text: str):
        self.flow.input_value = text
        self.flow.render()
