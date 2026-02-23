from PySide6.QtWidgets import QWidget, QVBoxLayout

from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.regex_dropdown import RegexDropdown
from comp382_assignment_2.gui.cfl_dropdown import CFLDropdown
from comp382_assignment_2.gui.language_inputbar import LanguageInputBar


class LangugageBuilder(QWidget):  # noqa: N801  (keep original spelling)
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.reg_dd = RegexDropdown(self.app_config)
        self.cfl_dd = CFLDropdown(self.app_config)
        self.input_bar = LanguageInputBar(self.app_config)

        layout.addWidget(self.reg_dd)
        layout.addWidget(self.cfl_dd)
        layout.addWidget(self.input_bar)
        layout.addStretch()
