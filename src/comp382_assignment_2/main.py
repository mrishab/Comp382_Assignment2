import sys
from PySide6.QtWidgets import QApplication
from comp382_assignment_2.gui.main_window import MainWindow
from comp382_assignment_2.gui.app_config import AppConfig

def main():
    app = QApplication(sys.argv)
    app_config = AppConfig()
    window = MainWindow(app_config)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()