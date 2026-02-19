from PySide6.QtWidgets import QPushButton, QLineEdit
from PySide6.QtCore import Qt
from comp382_assignment_2.gui.utils import load_stylesheet

class KeyboardButton(QPushButton):
    def __init__(self, text, target_input: QLineEdit, parent=None):
        super().__init__(text, parent)
        self.target_input = target_input
        self.setup_ui()
        self.clicked.connect(self.on_clicked)

    def setup_ui(self):
        self.setStyleSheet(load_stylesheet('keyboard_button.css'))
        self.setFixedSize(40, 40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def on_clicked(self):
        self.target_input.insert(self.text())
        self.target_input.setFocus()

class BackspaceButton(KeyboardButton):
    def __init__(self, target_input: QLineEdit, parent=None):
        super().__init__("⌫", target_input, parent)

    def on_clicked(self):
        self.target_input.backspace()
        self.target_input.setFocus()
