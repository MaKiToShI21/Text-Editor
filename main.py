from PyQt6.QtWidgets import QApplication
from text_editor import TextEditor
import sys


def main():
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
