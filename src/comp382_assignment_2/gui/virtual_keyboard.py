from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit
from comp382_assignment_2.gui.keyboard_button import KeyboardButton, BackspaceButton

class VirtualKeyboard(QWidget):
    def __init__(self, keys, target_input: QLineEdit, parent=None):
        super().__init__(parent)
        self.keys = keys
        self.target_input = target_input
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(5)
        self.setLayout(layout)

        # Add character keys
        for key in self.keys:
            btn = KeyboardButton(key, self.target_input)
            layout.addWidget(btn)

        # Add Backspace key
        backspace_btn = BackspaceButton(self.target_input)
        layout.addWidget(backspace_btn)

        layout.addStretch() # Push left alignment
