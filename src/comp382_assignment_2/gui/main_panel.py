from comp382_assignment_2.gui.separator import Separator
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.header import Header
from comp382_assignment_2.gui.section_step_1 import SectionStep1
from comp382_assignment_2.gui.section_step_2 import SectionStep2
from comp382_assignment_2.gui.utils import load_stylesheet

class MainPanel(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(load_stylesheet('main_panel.css'))
        self.setObjectName("MainPanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        self.header = Header(self.app_config)

        # Step 1 Section
        self.step1 = SectionStep1(self.app_config)

        # Horizontal Line Separator
        separator = Separator()

        # Step 2 Section
        self.step2 = SectionStep2(self.app_config)

        # Connecting the input bars of the two steps so they sync in realtime
        self.step1.regex_input_bar.textChanged.connect(self.step2.update_match)

        layout.addWidget(self.header)
        layout.addWidget(self.step1)
        layout.addWidget(separator)
        layout.addWidget(self.step2)

        # Spacer
        layout.addStretch()
