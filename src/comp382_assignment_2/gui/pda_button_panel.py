from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel

from comp382_assignment_2.common.colors import Color
from comp382_assignment_2.common.status import Status
from comp382_assignment_2.gui.app_config import AppConfig

_BTN_STYLE = (
    f"QPushButton {{ background:{Color.BUTTON_BG.value}; color:white; border:1px solid {Color.BUTTON_BORDER.value}; "
    "border-radius:5px; font-size:13px; font-weight:bold; padding: 0 12px; }"
    f"QPushButton:hover {{ background:{Color.BUTTON_HOVER_BG.value}; }}"
    f"QPushButton:pressed {{ background:{Color.BUTTON_PRESSED_BG.value}; }}"
)


class PDAButtonPanel(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.next_btn = QPushButton(self.app_config.step_btn)
        self.reset_btn = QPushButton(self.app_config.reset_btn)

        for button in (self.next_btn, self.reset_btn):
            button.setFixedHeight(32)
            button.setStyleSheet(_BTN_STYLE)
            layout.addWidget(button)

        layout.addStretch()

        self.status_label = QLabel(Status.IDLE.value)
        self.status_label.setStyleSheet(
            f"color:{Color.STATUS_IDLE_TEXT.value}; font-size:12px; padding:2px 8px; "
            f"border:1px solid {Color.STATUS_IDLE_BORDER.value}; border-radius:3px;"
        )
        layout.addWidget(self.status_label)

    def set_status(self, status: str | Status):
        palette = {
            Status.ACCEPTED.value: Color.NODE_ACCEPTED_BG.value,
            Status.REJECTED.value: Color.NODE_REJECTED_BG.value,
            Status.RUNNING.value: Color.NODE_ACTIVE_BG.value,
            Status.IDLE.value: Color.STATUS_IDLE_TEXT.value,
        }
        normalized_status = status.value if isinstance(status, Status) else status.lower()
        colour = palette.get(normalized_status, Color.STATUS_IDLE_TEXT.value)
        self.status_label.setText(normalized_status)
        self.status_label.setStyleSheet(
            f"color:{colour}; font-size:12px; padding:2px 8px;"
            f"border:1px solid {colour}; border-radius:3px;"
        )
