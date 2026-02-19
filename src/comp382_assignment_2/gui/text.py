from PySide6.QtWidgets import QLabel

class Text(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setWordWrap(True)
