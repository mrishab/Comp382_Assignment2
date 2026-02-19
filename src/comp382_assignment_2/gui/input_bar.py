from comp382_assignment_2.gui.utils import load_stylesheet
from PySide6.QtWidgets import QWidget, QHBoxLayout
from comp382_assignment_2.gui.status_indicator import StatusIndicator
from comp382_assignment_2.gui.validated_line_edit import ValidatedLineEdit

class InputBar(QWidget):
    def __init__(self, placeholder_text="", allowed_chars=None, valid_text="", invalid_text="", empty_text="", validator_func=None, parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder_text
        self.allowed_chars = allowed_chars
        self.valid_text = valid_text
        self.invalid_text = invalid_text
        self.empty_text = empty_text
        self.validator_func = validator_func if validator_func is not None else lambda text: True
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(load_stylesheet('input_bar.css'))
        self.setObjectName("InputBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Input Field
        self.input_field = ValidatedLineEdit(allowed_chars=self.allowed_chars)
        self.input_field.setPlaceholderText(self.placeholder_text)

        # Validate Button
        self.status_indicator = StatusIndicator()

        # Connect internal signals
        self.input_field.textChanged.connect(self._on_text_changed)

        # Initial status
        self._on_text_changed(self.input_field.text())

        layout.addWidget(self.input_field)
        layout.addWidget(self.status_indicator)

    def _on_text_changed(self, text):
        is_valid = self.validator_func(text)
        self.status_indicator.set_status(is_valid, self.empty_text, self.valid_text, self.invalid_text)

    # Exposting inner input field properties for access from this class
    @property
    def textChanged(self):
        return self.input_field.textChanged

    def refresh_validation(self):
        self._on_text_changed(self.input_field.text())

    def text(self):
        return self.input_field.text()