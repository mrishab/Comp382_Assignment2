from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.validated_line_edit import ValidatedLineEdit
from comp382_assignment_2.gui.virtual_keyboard import VirtualKeyboard
from comp382_assignment_2.common.symbols import STRING_SYMBOLS


class LanguageInputBar(QFrame):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("LanguageInputBar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        input_label = QLabel(self.app_config.input_label)
        input_label.setStyleSheet("color: #ccc; font-size: 12px;")
        layout.addWidget(input_label)

        self.input_field = ValidatedLineEdit(allowed_chars=STRING_SYMBOLS)
        self.input_field.setPlaceholderText(self.app_config.input_placeholder)
        self.input_field.setStyleSheet(
            "background:#ffffff; color:#222; border:1px solid #555; "
            "border-radius:4px; padding:6px; font-size:14px;"
        )
        layout.addWidget(self.input_field)

        self.keyboard = VirtualKeyboard(STRING_SYMBOLS, self.input_field)
        layout.addWidget(self.keyboard)
