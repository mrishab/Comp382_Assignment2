from PySide6.QtWidgets import QLabel

from comp382_assignment_2.gui.utils import load_stylesheet


class Heading1(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("Heading1")
        self.setStyleSheet(load_stylesheet("heading1.css"))
