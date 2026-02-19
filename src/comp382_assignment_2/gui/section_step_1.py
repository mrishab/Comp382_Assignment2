from comp382_assignment_2.gui.regex_sample_dropdown import RegexSampleDropdown
from comp382_assignment_2.common.symbols import REGEX_SYMBOLS
from comp382_assignment_2.gui.input_bar import InputBar
from comp382_assignment_2.gui.text import Text
from comp382_assignment_2.gui.heading_label import HeadingLabel
from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox
from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.virtual_keyboard import VirtualKeyboard

class SectionStep1(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 20, 0, 20)
        self.setLayout(layout)

        # 1. Heading
        self.heading = HeadingLabel(self.app_config.section_1_heading)

        # "Enter R:" Label
        self.sub_label = Text(self.app_config.section_1_subheading)

        # Regex Input Bar
        self.regex_input_bar = InputBar(
            placeholder_text=self.app_config.section_1_input_placeholder,
            allowed_chars=REGEX_SYMBOLS,
            empty_text=self.app_config.section_1_status_text_empty,
            valid_text=self.app_config.section_1_status_text_valid,
            invalid_text=self.app_config.section_1_status_text_invalid,
            # validator_func=lambda input_text: validate_regex(input_text)
        )

        self.regex_sample_dropdown = RegexSampleDropdown(self.app_config, self.regex_input_bar)

        # Virtual Keyboard
        self.keyboard = VirtualKeyboard(REGEX_SYMBOLS, self.regex_input_bar.input_field)

        layout.addWidget(self.heading)
        layout.addWidget(self.sub_label)
        layout.addWidget(self.regex_sample_dropdown)
        layout.addWidget(self.regex_input_bar)
        layout.addWidget(self.keyboard)
