from PySide6.QtWidgets import QLabel

from comp382_assignment_2.gui.utils import load_stylesheet


class FieldLabel(QLabel):
    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("FieldLabel")
        self.setStyleSheet(load_stylesheet("label.css"))
