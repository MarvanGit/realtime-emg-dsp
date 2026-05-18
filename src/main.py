import sys
import os
from PySide6.QtWidgets import QApplication

# Adjust the system path to ensure that the core modules can be imported correctly
# This is necessary because the core modules are located in a different directory than the main script.
# The following code calculates the project root directory and appends it to the system path.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.ui.main_window import MainWindow

def main():
    """
    The main function initializes the QApplication and creates an instance of the MainWindow.
    It starts the application's event loop, allowing the user interface to function and respond to user interactions.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()