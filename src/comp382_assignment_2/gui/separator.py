from comp382_assignment_2.gui.utils import load_stylesheet
from PySide6.QtWidgets import QFrame

class Separator(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(load_stylesheet('separator.css'))
        self.setObjectName("Separator")
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)