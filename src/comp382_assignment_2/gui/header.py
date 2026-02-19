from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.utils import load_stylesheet

class Header(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(load_stylesheet('header.css'))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header Title
        self.header_title = QLabel(self.app_config.header_title)
        self.header_title.setObjectName("HeaderTitle")

        # Subtitle Text
        self.subtitle_label = QLabel(self.app_config.header_subtitle)
        self.subtitle_label.setObjectName("SubtitleLabel")

        layout.addWidget(self.header_title)
        layout.addWidget(self.subtitle_label)
