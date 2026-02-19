from comp382_assignment_2.gui.utils import load_stylesheet
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class StatusIndicator(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("StatusIndicator")
        self.setStyleSheet(load_stylesheet('status_indicator.css'))
        self.setFixedWidth(140)
        self.setCheckable(False)
        self.setCursor(Qt.CursorShape.ArrowCursor)


    def set_status(self, is_valid: bool, empty_text: str, success_text: str, failure_text: str):
        if is_valid is None:
            self.setText(empty_text)
            self.setProperty("valid", None)
        elif is_valid:
            self.setText(success_text)
            self.setProperty("valid", True)
        else:
            self.setText(failure_text)
            self.setProperty("valid", False)

        # Refresh style to apply variations if defined in CSS
        self.style().unpolish(self)
        self.style().polish(self)
