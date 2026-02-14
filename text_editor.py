from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QTabWidget, QFileDialog, QMessageBox,
                             QListWidget)
from PyQt6.uic import loadUi
from PyQt6.QtGui import QAction
import sys
import os


class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('text_editor.ui', self)

        self.setup_actions()

        self.input_tab_widget = self.findChild(QTabWidget, 'inputTabWidget')
        self.input_tab_widget.setTabsClosable(True)
        self.input_tab_widget.tabCloseRequested.connect(self.close_tab)

        self.output_tab_widget = self.findChild(QTabWidget, 'outputTabWidget')
        self.output_tab_widget.setTabsClosable(True)
        self.output_tab_widget.tabCloseRequested.connect(self.close_tab)

        self.file_paths = {}

    def setup_actions(self):
        # File actions
        self.actionOpen = self.findChild(QAction, 'actionOpen')
        if self.actionOpen:
            self.actionOpen.triggered.connect(self.open_file)

        self.actionNew = self.findChild(QAction, 'actionNew')
        if self.actionNew:
            self.actionNew.triggered.connect(self.new_file)

        self.actionSave = self.findChild(QAction, 'actionSave')
        if self.actionSave:
            self.actionSave.triggered.connect(self.save_file)

        self.actionSaveAs = self.findChild(QAction, 'actionSaveAs')
        if self.actionSaveAs:
            self.actionSaveAs.triggered.connect(self.save_file_as)

        self.actionExit = self.findChild(QAction, 'actionExit')
        if self.actionExit:
            self.actionExit.triggered.connect(self.close)

        # Run action
        self.actionExit = self.findChild(QAction, 'actionRun')
        if self.actionExit:
            self.actionExit.triggered.connect(self.run)

        # Edit actions
        self.actionUndo = self.findChild(QAction, 'actionUndo')
        if self.actionUndo:
            self.actionUndo.triggered.connect(self.undo)

        self.actionRedo = self.findChild(QAction, 'actionRedo')
        if self.actionUndo:
            self.actionRedo.triggered.connect(self.redo)

        self.actionCopy = self.findChild(QAction, 'actionCopy')
        if self.actionCopy:
            self.actionCopy.triggered.connect(self.copy)

        self.actionPaste = self.findChild(QAction, 'actionPaste')
        if self.actionPaste:
            self.actionPaste.triggered.connect(self.paste)

        self.actionCut = self.findChild(QAction, 'actionCut')
        if self.actionCut:
            self.actionCut.triggered.connect(self.cut)

        self.actionDelete = self.findChild(QAction, 'actionDelete')
        if self.actionDelete:
            self.actionDelete.triggered.connect(self.delete)

        self.actionSelectAll = self.findChild(QAction, 'actionSelectAll')
        if self.actionSelectAll:
            self.actionSelectAll.triggered.connect(self.select_all)

    def close_tab(self, index):
        text_edit = self.input_tab_widget.widget(index)
        tab_name = self.input_tab_widget.tabText(index)

        if text_edit.document().isModified():
            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                "Сохранить изменения перед закрытием?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.input_tab_widget.setCurrentIndex(index)
                saved = self.save_file()
                if not saved:
                    return
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        if id(text_edit) in self.file_paths:
            del self.file_paths[id(text_edit)]

        self.input_tab_widget.removeTab(index)
        text_edit.deleteLater()

        self.statusBar.showMessage(f"{tab_name} успешно закрыт", 3000)

    def open_file(self):
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            "Выберите файл для открытия",
            "",
            "*.*"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                file_name = os.path.basename(file_path)
                self.create_new_tab(file_name, content, file_path)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось открыть файл:\n{str(e)}")

    def create_new_tab(self, title="Новый документ", content="",
                       file_path=None):
        text_edit = QTextEdit()
        text_edit.setPlainText(content)

        index = self.input_tab_widget.addTab(text_edit, title)

        if file_path:
            self.file_paths[id(text_edit)] = file_path

        self.input_tab_widget.setCurrentIndex(index)

        self.statusBar.showMessage(f"{title} успешно открыт", 3000)

        return text_edit

    def new_file(self):
        self.create_new_tab()

    def save_file(self):
        text_edit = self.input_tab_widget.currentWidget()

        if not text_edit:
            return

        file_path = self.file_paths.get(id(text_edit))

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_edit.toPlainText())

                self.statusBar.showMessage(
                    f"Файл{os.path.basename(file_path)} сохранен", 2000)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")
        else:
            self.save_file_as()

    def save_file_as(self):
        text_edit = self.input_tab_widget.currentWidget()

        if not text_edit:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл как",
                                                   "",
                                                   "Текстовые файлы (*.txt);;"
                                                   "doc (*.doc);;"
                                                   "docx (*.docx);;"
                                                   "PDF (*.pdf);;"
                                                   "rtf (*.rtf);;"
                                                   "Все файлы (*.*)")

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_edit.toPlainText())

                    self.file_paths[id(text_edit)] = file_path

                    index = self.input_tab_widget.currentIndex()
                    file_name = os.path.basename(file_path)
                    self.input_tab_widget.setTabText(index, file_name)

                    self.statusBar.showMessage(
                        f"Файл сохранен как {file_name}", 3000)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")

    def run(self):
        index = self.input_tab_widget.currentIndex()
        text_edit = self.input_tab_widget.widget(index)
        tab_name = self.input_tab_widget.tabText(index)

        lines = text_edit.toPlainText().split('\n')

        list_widget = QListWidget()

        for line in lines:
            if line.strip():
                list_widget.addItem(line)

        self.output_tab_widget.addTab(list_widget, tab_name)
        self.output_tab_widget.setCurrentIndex(
            self.output_tab_widget.count() - 1)

    def undo(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.undo()
            self.statusBar.showMessage("Отмена", 3000)

    def redo(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.redo()
            self.statusBar.showMessage("Повтор", 3000)

    def copy(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.copy()
            self.statusBar.showMessage("Скопировано", 2000)

    def paste(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.paste()
            self.statusBar.showMessage("Вставлено", 3000)

    def cut(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.cut()
            self.statusBar.showMessage("Вырезано", 2000)

    def delete(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            cursor = text_edit.textCursor()
            if cursor.hasSelection():
                cursor.removeSelectedText()
                self.statusBar.showMessage("Удалено", 2000)

    def select_all(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.selectAll()
            self.statusBar.showMessage("Выделено всё", 2000)

    def get_current_text_edit(self):
        if hasattr(self, 'input_tab_widget') and self.input_tab_widget:
            current_widget = self.input_tab_widget.currentWidget()
            if isinstance(current_widget, QTextEdit):
                return current_widget
            else:
                self.statusBar.showMessage("Текстовое поле не активно", 3000)
                return None
        return None


def main():
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
