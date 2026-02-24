from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.pda_button_panel import PDAButtonPanel
from comp382_assignment_2.gui.super_pda_view import SuperPDAView
from comp382_assignment_2.super_pda.base import BaseSuperPDA


class RightContentPanel(QWidget):
    """Right panel: section title + Super PDA graph view."""

    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("PdaContainer")
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(6)

        title = QLabel(self.app_config.super_pda_label)
        title.setStyleSheet("color:#ddd; font-size:14px; font-weight:bold;")
        root.addWidget(title)

        self.button_panel = PDAButtonPanel(self.app_config)
        root.addWidget(self.button_panel)

        self.filtered_input_label = QLabel("Filtered Input: --")
        self.filtered_input_label.setStyleSheet("color:#cfcfcf; font-size:12px;")
        root.addWidget(self.filtered_input_label)

        self.super_pda_view = SuperPDAView()
        root.addWidget(self.super_pda_view, stretch=1)

    def render_super_pda(self, super_pda: BaseSuperPDA):
        self.super_pda_view.render_graph(super_pda)

    def render_placeholder(self):
        self.super_pda_view.render_placeholder()

    def render_empty_language(self):
        self.super_pda_view.render_empty_language()

    def set_filtered_input_text(self, text: str):
        display = text if text else "--"
        self.filtered_input_label.setText(f"Filtered Input: {display}")

    def set_status(self, status: str):
        self.button_panel.set_status(status)
