from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from comp382_assignment_2.gui.app_config import AppConfig
from comp382_assignment_2.gui.main_panel import MainPanel


class MainWindow(QMainWindow):
    def __init__(self, app_config: AppConfig):
        super().__init__()
        self.app_config = app_config
        self.resize(app_config.window_width, app_config.window_height)
        self.setWindowTitle(app_config.window_title)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setLayout(layout)

        self.main_panel = MainPanel(app_config)
        layout.addWidget(self.main_panel, stretch=1)
