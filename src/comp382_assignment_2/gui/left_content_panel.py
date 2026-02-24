from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.language_builder import LangugageBuilder
from comp382_assignment_2.gui.flow_diagram import FlowDiagram
from comp382_assignment_2.gui.left_content_panel_controller import LeftContentPanelController


class LeftContentPanel(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.language_builder = LangugageBuilder(self.app_config)
        layout.addWidget(self.language_builder)

        self.flow = FlowDiagram()
        self.flow.setMinimumHeight(160)
        layout.addWidget(self.flow, stretch=1)

        self.controller = LeftContentPanelController(self.language_builder, self.flow)
