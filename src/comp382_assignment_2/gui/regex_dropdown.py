from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel

from comp382_assignment_2.gui.app_config import AppConfig


class RegexDropdown(QWidget):
    def __init__(self, app_config: AppConfig, parent=None):
        super().__init__(parent)
        self.app_config = app_config
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(self.app_config.dropdown_regular_label)
        label.setStyleSheet("color: #ccc; font-size: 12px;")
        layout.addWidget(label)

        self.combo = QComboBox()
        self.combo.addItem("Select regular language...")
        for key, info in self.app_config.regular_languages.items():
            self.combo.addItem(info["label"], key)
        layout.addWidget(self.combo)

    def currentData(self):
        return self.combo.currentData()

    @property
    def currentIndexChanged(self):
        return self.combo.currentIndexChanged