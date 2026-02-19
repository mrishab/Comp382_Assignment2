
from comp382_assignment_2.gui.utils import load_stylesheet
from PySide6.QtWidgets import QLabel

class HeadingLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(load_stylesheet('heading_label.css'))
        self.setObjectName("HeadingLabel")

