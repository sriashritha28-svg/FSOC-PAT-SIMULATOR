import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import FSOCMainWindow

def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    window = FSOCMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()