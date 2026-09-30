"""JARVIS AI v0.1 desktop entry point."""
import sys
from PySide6.QtWidgets import QApplication
from core.assistant import JarvisAssistant
from desktop_config import DATABASE_PATH
from interface.main_window import MainWindow
from interface.themes import THEME
from memory.database import Database
from memory.long_term import LongTermMemory

def main():
    application = QApplication(sys.argv)
    application.setApplicationName('JARVIS AI')
    application.setApplicationVersion('0.1.0')
    application.setStyleSheet(THEME)
    memory = LongTermMemory(Database(DATABASE_PATH))
    window = MainWindow(JarvisAssistant(), memory)
    window.show()
    sys.exit(application.exec())

if __name__ == '__main__':
    main()