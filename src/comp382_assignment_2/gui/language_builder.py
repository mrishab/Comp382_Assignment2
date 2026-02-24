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

    @property
    def input_field(self):
        return self.input_bar.input_field

    @property
    def keyboard(self):
        return self.input_bar.keyboard

    def connect_inputs(self, on_dropdown_changed, on_input_changed):
        self.reg_dd.currentIndexChanged.connect(on_dropdown_changed)
        self.cfl_dd.currentIndexChanged.connect(on_dropdown_changed)
        self.input_field.textChanged.connect(on_input_changed)

    def selected_reg_key(self):
        return self.reg_dd.currentData()

    def selected_cfl_key(self):
        return self.cfl_dd.currentData()

    def selected_reg_label(self) -> str:
        key = self.selected_reg_key()
        if not key:
            return ""
        return self.app_config.regular_languages.get(key, {}).get("pattern", "")

    def selected_cfl_label(self) -> str:
        key = self.selected_cfl_key()
        if not key:
            return ""
        return self.app_config.context_free_languages.get(key, {}).get("pattern", "")
