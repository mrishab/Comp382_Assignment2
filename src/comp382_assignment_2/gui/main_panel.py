from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.header import Header
from comp382_assignment_2.gui.utils import load_stylesheet
from comp382_assignment_2.gui.content_panel import ContentPanel
from comp382_assignment_2.gui.language_builder_controller import LanguageBuilderController


class MainPanel(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
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

        self.language_builder_controller = LanguageBuilderController(
            app_config=self.app_config,
            language_builder=content.left.language_builder,
            flow=content.left.flow,
            right_panel=content.right,
            pda_view=content.right.pda_view,
            parent=self,
        )
