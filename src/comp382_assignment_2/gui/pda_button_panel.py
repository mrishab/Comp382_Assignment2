from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel

from comp382_assignment_2.gui.app_config import AppConfig

_BTN_STYLE = (
    "QPushButton { background:#495057; color:white; border:1px solid #6c757d; "
    "border-radius:5px; font-size:13px; font-weight:bold; padding: 0 12px; }"
    "QPushButton:hover { background:#6c757d; }"
    "QPushButton:pressed { background:#343a40; }"
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

        self.status_label = QLabel("--")
        self.status_label.setStyleSheet(
            "color:#888; font-size:12px; padding:2px 8px; "
            "border:1px solid #444; border-radius:3px;"
        )
        layout.addWidget(self.status_label)

    def set_status(self, status: str):
        palette = {
            "accepted": "#5CB85C",
            "rejected": "#E74C3C",
            "running": "#FFD700",
            "--": "#888",
        }
        colour = palette.get(status.lower(), "#888")
        self.status_label.setText(status)
        self.status_label.setStyleSheet(
            f"color:{colour}; font-size:12px; padding:2px 8px;"
            f"border:1px solid {colour}; border-radius:3px;"
        )
