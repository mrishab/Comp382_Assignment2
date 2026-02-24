from PySide6.QtWidgets import QWidget, QHBoxLayout

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.left_content_panel import LeftContentPanel
from comp382_assignment_2.gui.right_content_panel import RightContentPanel
from comp382_assignment_2.gui.content_panel_controller import ContentPanelController


class ContentPanel(QWidget):

    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.left = LeftContentPanel(self.app_config)
        self.right = RightContentPanel(self.app_config)

        layout.addWidget(self.left, stretch=1)
        layout.addWidget(self.right, stretch=1)

        self.controller = ContentPanelController(self.app_config, self)
