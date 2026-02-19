from comp382_assignment_2.gui.heading_label import HeadingLabel
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.text import Text
from comp382_assignment_2.gui.utils import load_stylesheet

class LeftSidebar(QFrame):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(load_stylesheet('left_sidebar.css'))
        self.setFixedWidth(250)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        # Title
        title_label = HeadingLabel(self.app_config.left_sidebar_title)
        layout.addWidget(title_label)

        # Separator or spacing
        layout.addSpacing(10)

        # Reference Points
        for text in self.app_config.left_sidebar_info_points:
            text_label = Text(text)
            layout.addWidget(text_label)

        # Add stretch at the bottom to push content up
        layout.addStretch()
