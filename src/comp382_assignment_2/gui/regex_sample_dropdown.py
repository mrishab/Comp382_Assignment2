from comp382_assignment_2.common.regex_samples import RegexSamples
from comp382_assignment_2.gui.app_config import AppConfig
from PySide6.QtWidgets import QComboBox

class RegexSampleDropdown(QComboBox):
    def __init__(self, app_config: AppConfig, regex_input_bar, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.regex_input_bar = regex_input_bar
        self.setup_ui()

    def setup_ui(self):
        self.setPlaceholderText(self.app_config.practice_examples_placeholder)
        self.addItem(self.app_config.practice_examples_placeholder) # Index 0

        # Populate Dropdown
        for sample in RegexSamples:
            description = self.app_config.practice_examples_samples_descriptions.get(sample.description_key, "<missing description>")
            label = f"{sample.pattern}  -  {description}"
            self.addItem(label, sample.pattern)

        self.currentIndexChanged.connect(self._on_example_selected)

    def _on_example_selected(self, index):
        if index > 0: # Ignoring the first selection
            regex = self.itemData(index)
            if regex:
                self.regex_input_bar.input_field.setText(regex)