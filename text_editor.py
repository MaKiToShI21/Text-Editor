from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QTabWidget, QFileDialog, QMessageBox,
                             QListWidget, QDialog, QTextBrowser,
                             QVBoxLayout)
from PyQt6.QtGui import QAction, QColor, QDragEnterEvent, QDropEvent
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.uic import loadUi
import sys
import os
# from ui_editor import Ui_MainWindow


class TextEditor(QMainWindow):  # , Ui_MainWindow
    def __init__(self):
        super().__init__()
        loadUi('text_editor.ui', self)
        # self.setupUi(self)

        self.setAcceptDrops(True)
        self.setup_actions()

        self.input_tab_widget = self.findChild(QTabWidget, 'inputTabWidget')
        self.input_tab_widget.tabCloseRequested.connect(self.close_tab)

        self.output_tab_widget = self.findChild(QTabWidget, 'outputTabWidget')
        self.output_tab_widget.tabCloseRequested.connect(self.close_tab)

        self.status_bar = self.statusBar
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

        # Reference actions
        self.actionAbout = self.findChild(QAction, 'actionAbout')
        if self.actionAbout:
            self.actionAbout.triggered.connect(self.about)

        self.actionHelp = self.findChild(QAction, 'actionHelp')
        if self.actionHelp:
            self.actionHelp.triggered.connect(self.help)

    def dragEnterEvent(self, event: QDragEnterEvent | None):
        if event is None:
            return

        mime_data = event.mimeData()
        if mime_data is None:
            return

        if mime_data.hasUrls():
            event.acceptProposedAction()
            self.status_bar.showMessage("Отпустите файл для открытия", 0)
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.status_bar.clearMessage()
        event.accept()

    def dropEvent(self, event: QDropEvent | None):
        if event is None:
            return

        mime_data = event.mimeData()
        if mime_data is None:
            return

        files = [u.toLocalFile() for u in mime_data.urls()
                 if u.isLocalFile()]

        if files:
            self.status_bar.showMessage(f"Открываю {len(files)} файлов...", 0)
            QApplication.processEvents()

            opened = 0
            for file_path in files:
                if os.path.isfile(file_path):
                    if self.open_dropped_file(file_path):
                        opened += 1

            self.status_bar.showMessage(f"Открыто файлов: {opened}", 3000)

        event.acceptProposedAction()

    def open_dropped_file(self, file_path):
        try:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                file_name = os.path.basename(file_path)
                self.create_new_tab(file_name, content, file_path)
                return True
            except UnicodeDecodeError as e:
                QMessageBox.critical(
                    self, "Ошибка",
                    f"Не удалось открыть файл (ошибка кодировки):\n{str(e)}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Ошибка",
                                 f"Не удалось открыть файл:\n{str(e)}")
            return False

    def close_tab(self, index):
        text_edit = self.input_tab_widget.widget(index)
        tab_name = self.input_tab_widget.tabText(index)

        if text_edit.isModified():
            reply = QMessageBox.question(
                self,
                "Несохраненные изменения",
                f"Сохранить изменения в '{tab_name}' перед закрытием?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.input_tab_widget.setCurrentIndex(index)

                saved = self.save_file()

                if not saved:
                    self.status_bar.showMessage("Закрытие вкладки отменено",
                                                3000)
                    return

            elif reply == QMessageBox.StandardButton.Cancel:
                self.status_bar.showMessage("Закрытие вкладки отменено", 3000)
                return

        if id(text_edit) in self.file_paths:
            del self.file_paths[id(text_edit)]

        self.input_tab_widget.removeTab(index)
        text_edit.deleteLater()

        self.status_bar.showMessage(f"Вкладка '{tab_name}' закрыта", 3000)

    def close(self):
        for i in range(self.input_tab_widget.count()):
            text_edit = self.input_tab_widget.widget(i)
            if text_edit.isModified():
                tab_name = self.input_tab_widget.tabText(i)

                reply = QMessageBox.question(
                    self,
                    "Несохраненные изменения",
                    f"Вкладка '{tab_name}' содержит несохраненные изменения.\n"
                    "Сохранить перед выходом?",
                    QMessageBox.StandardButton.Save |
                    QMessageBox.StandardButton.Discard |
                    QMessageBox.StandardButton.Cancel
                )

                if reply == QMessageBox.StandardButton.Save:
                    self.input_tab_widget.setCurrentIndex(i)
                    saved_file = self.save_file()
                    if not saved_file:
                        return
                elif reply == QMessageBox.StandardButton.Cancel:
                    return
        super().close()

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
        text_edit = CodeEditor()
        text_edit.setText(content)

        index = self.input_tab_widget.addTab(text_edit, title)

        if file_path:
            self.file_paths[id(text_edit)] = file_path
            text_edit.setModified(False)

        self.input_tab_widget.setCurrentIndex(index)

        self.status_bar.showMessage(f"{title} успешно открыт", 3000)

        return text_edit

    def new_file(self):
        self.create_new_tab()

    def save_file(self):
        text_edit = self.input_tab_widget.currentWidget()

        if not text_edit:
            return False

        file_path = self.file_paths.get(id(text_edit))

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(text_edit.text())

                text_edit.setModified(False)

                self.status_bar.showMessage(
                    f"Файл {os.path.basename(file_path)} сохранен", 2000)

                return True

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        text_edit = self.input_tab_widget.currentWidget()

        if not text_edit:
            return False

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
                    file.write(text_edit.text())

                self.file_paths[id(text_edit)] = file_path

                text_edit.setModified(False)

                index = self.input_tab_widget.currentIndex()
                file_name = os.path.basename(file_path)
                self.input_tab_widget.setTabText(index, file_name)

                self.status_bar.showMessage(f"Файл сохранен как {file_name}",
                                            3000)

                return True

            except Exception as e:
                QMessageBox.critical(self, "Ошибка",
                                     f"Не удалось сохранить файл: {str(e)}")
                return False
        else:
            self.status_bar.showMessage("Сохранение отменено", 2000)
            return False

    def run(self):
        if hasattr(self, 'text_edit') and self.text_edit:
            index = self.input_tab_widget.currentIndex()
            text_edit = self.input_tab_widget.widget(index)
            tab_name = self.input_tab_widget.tabText(index)

            lines = text_edit.text().split('\n')

            list_widget = QListWidget()

            for line in lines:
                if line.strip():
                    list_widget.addItem(line)

            self.output_tab_widget.addTab(list_widget, tab_name)
            self.output_tab_widget.setCurrentIndex(
                self.output_tab_widget.count() - 1)
        return None

    def undo(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.undo()
            self.status_bar.showMessage("Отмена", 3000)

    def redo(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.redo()
            self.status_bar.showMessage("Повтор", 3000)

    def copy(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.copy()
            self.status_bar.showMessage("Скопировано", 2000)

    def paste(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.paste()
            self.status_bar.showMessage("Вставлено", 3000)

    def cut(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.cut()
            self.status_bar.showMessage("Вырезано", 2000)

    def delete(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            if text_edit.hasSelectedText():
                text_edit.removeSelectedText()
                self.status_bar.showMessage("Удалено", 2000)

    def select_all(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.selectAll()
            self.status_bar.showMessage("Выделено всё", 2000)

    def get_current_text_edit(self):
        if hasattr(self, 'input_tab_widget') and self.input_tab_widget:
            current_widget = self.input_tab_widget.currentWidget()
            if isinstance(current_widget, (QTextEdit, QsciScintilla)):
                return current_widget
            else:
                self.status_bar.showMessage("Текстовое поле не активно", 3000)
                return None
        return None

    def help(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Руководство пользователя")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)

        dialog.setStyleSheet("background-color: #2b2b2b;")

        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        text_browser.setHtml("""
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    color: #ffffff;
                    background-color: #2b2b2b;
                }
                h1 {
                    color: #ffffff;
                    text-align: center;
                    margin-bottom: 5px;
                }
                h2 {
                    color: #ffffff;
                    border-bottom: 2px solid #404040;
                    padding-bottom: 8px;
                    margin-top: 25px;
                }
                h3 {
                    color: #ffffff;
                    margin-top: 20px;
                }
                .version {
                    color: #a0a0a0;
                    font-size: 14px;
                    text-align: center;
                    margin-bottom: 5px;
                }
                .section {
                    margin: 15px 0;
                }
                .menu-path {
                    color: #a0a0a0;
                    font-style: italic;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                th {
                    background-color: #333333;
                    padding: 10px;
                    text-align: left;
                    border: 1px solid #404040;
                    color: #ffffff;
                }
                td {
                    padding: 8px 10px;
                    border: 1px solid #404040;
                    color: #ffffff;
                }
                .footer {
                    border-top: 1px solid #404040;
                    padding-top: 15px;
                    margin-top: 25px;
                    color: #a0a0a0;
                    font-size: 12px;
                    text-align: center;
                }
                ul {
                    line-height: 1.6;
                }
                a {
                    color: #88c0ff;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <h1>Текстовый редактор</h1>
            <div class='version'>Руководство пользователя | Версия 1.0</div>

            <h2 id='intro'>Введение</h2>
            <p><b>Текстовый редактор</b> — это приложение для создания и редактирования текстовых документов с возможностью синтаксического анализа. Программа предоставляет удобный интерфейс для работы с текстом и поддерживает все основные операции редактирования.</p>

            <h2 id='interface'>Интерфейс программы</h2>
            <p>Главное окно текстового редактора состоит из следующих элементов:</p>
            <ul>
                <li><b>Заголовок окна</b> — отображает название программы и имя текущего файла</li>
                <li><b>Главное меню</b> — содержит все доступные команды</li>
                <li><b>Панель инструментов</b> — кнопки быстрого доступа</li>
                <li><b>Область редактирования</b> — текстовое поле для ввода и редактирования текста</li>
                <li><b>Область вывода результатов</b> — область для отображения результатов работы анализатора</li>
                <li><b>Строка состояния</b> — отображает информацию о состоянии работы приложения</li>
            </ul>

            <h2 id='file-menu'>Меню «Файл»</h2>
            <table>
                <tr>
                    <th>Команда</th>
                    <th>Горячая клавиша</th>
                    <th>Описание</th>
                </tr>
                <tr>
                    <td><b>Создать</b></td>
                    <td><span>Ctrl+N</span=></td>
                    <td>Создает новый документ в новой вкладке</td>
                </tr>
                <tr>
                    <td><b>Открыть</b></td>
                    <td><span>Ctrl+O</span></td>
                    <td>Открывает существующий текстовый файл</td>
                </tr>
                <tr>
                    <td><b>Сохранить</b></td>
                    <td><span>Ctrl+S</span></td>
                    <td>Сохраняет текущий документ</td>
                </tr>
                <tr>
                    <td><b>Сохранить как</b></td>
                    <td><span>Ctrl+Shift+S</span></td>
                    <td>Сохраняет документ под новым именем</td>
                </tr>
                <tr>
                    <td><b>Выход</b></td>
                    <td><span>Ctrl+Q</span></td>
                    <td>Завершает работу программы</td>
                </tr>
            </table>

            <p>При попытке закрыть несохраненный документ программа предложит сохранить изменения.</p>

            <h2 id='edit-menu'>Меню «Правка»</h2>
            <table>
                <tr>
                    <th>Команда</th>
                    <th>Горячая клавиша</th>
                    <th>Описание</th>
                </tr>
                <tr>
                    <td><b>Отменить</b></td>
                    <td><span>Ctrl+Z</span></td>
                    <td>Отменяет последнее действие</td>
                </tr>
                <tr>
                    <td><b>Повторить</b></td>
                    <td><span>Ctrl+Y</span></td>
                    <td>Повторяет отмененное действие</td>
                </tr>
                <tr>
                    <td><b>Вырезать</b></td>
                    <td><span>Ctrl+X</span></td>
                    <td>Копирует выделенный текст в буфер и удаляет его</td>
                </tr>
                <tr>
                    <td><b>Копировать</b></td>
                    <td><span>Ctrl+C</span></td>
                    <td>Копирует выделенный текст в буфер обмена</td>
                </tr>
                <tr>
                    <td><b>Вставить</b></td>
                    <td><span>Ctrl+V</span></td>
                    <td>Вставляет текст из буфера обмена</td>
                </tr>
                <tr>
                    <td><b>Удалить</b></td>
                    <td><span>Del</span></td>
                    <td>Удаляет выделенный текст</td>
                </tr>
                <tr>
                    <td><b>Выделить все</b></td>
                    <td><span>Ctrl+A</span></td>
                    <td>Выделяет весь текст в документе</td>
                </tr>
            </table>

            <h2 id='text-menu'>Меню «Текст»</h2>
            <p>Меню «Текст» содержит информационные разделы о языке и грамматике:</p>
            <ul>
                <li><b>Постановка задачи</b> — описание цели и задач работы</li>
                <li><b>Грамматика</b> — формальное описание грамматики языка</li>
                <li><b>Классификация грамматики</b> — тип грамматики по Хомскому</li>
                <li><b>Метод анализа</b> — описание метода синтаксического анализа</li>
                <li><b>Тестовый пример</b> — пример разбора входной строки</li>
                <li><b>Список литературы</b> — использованные источники</li>
                <li><b>Исходный код программы</b> — код приложения</li>
            </ul>
            <p>При выборе любого пункта открывается окно с соответствующей информацией.</p>

            <h2 id='run-menu'>Меню «Пуск»</h2>
            <p><b>Запуск анализатора</b> (<span>F5</span>) — запускает синтаксический анализ текста из области редактирования.</p>

            <p><b>Результаты анализа:</b></p>
            <ul>
                <li>Ошибочные строки отмечаются красным цветом с указанием позиции ошибки</li>
                <li>При щелчке на сообщении об ошибке курсор переходит к ошибочному фрагменту</li>
            </ul>

            <h2 id='help-menu'>Меню «Справка»</h2>
            <table>
                <tr>
                    <th>Команда</th>
                    <th>Горячая клавиша</th>
                    <th>Описание</th>
                </tr>
                <tr>
                    <td><b>Вызов справки</b></td>
                    <td><span>F1</span></td>
                    <td>Открывает данное руководство пользователя</td>
                </tr>
                <tr>
                    <td><b>О программе</b></td>
                    <td>F2</td>
                    <td>Информация о программе и разработчике</td>
                </tr>
            </table>

            <h2>Работа с областями редактирования и вывода</h2>
            <p><b>Область редактирования:</b> предназначена для ввода и редактирования текста. Поддерживаются все стандартные операции редактирования.</p>
            <p><b>Область вывода результатов:</b> отображает результаты работы синтаксического анализатора. Область доступна только для чтения.</p>
            <p><b>Изменение размеров областей:</b> перетаскивайте разделитель между областями мышью.</p>

            <div class='footer'>
                <p>Разработано с использованием PyQt6</p>
                <p>© 2026 MaKiToShI</p>
            </div>
        </body>
        </html>
        """)

        text_browser.setOpenExternalLinks(True)
        text_browser.setReadOnly(True)
        layout.addWidget(text_browser)
        dialog.exec()

    def about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("О программе")
        dialog.setMinimumWidth(450)
        dialog.setMinimumHeight(350)

        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        text_browser.setHtml("""
        <div style='text-align: center;'>
            <h1>Текстовый редактор</h1>
            <p style='color: #868e94; font-size: 14px;'>Версия 1.0</p>

            <div style='padding: 5px;'>
                <p style='font-size: 16px; line-height: 1;'>
                    Программа для редактирования текстовых файлов<br>
                    с возможностью синтаксического анализа
                </p>
            </div>

            <div>
                <p><b>Разработчик:</b> MaKiToShI</p>
                <p><b>Год:</b> 2026</p>
            </div>

            <div style='border-top: 1px solid #dee2e6; padding-top: 15px;'>
                <p style='color: #868e94; font-size: 12px;'>
                    Разработано с использованием PyQt6<br>
                    © 2026 MaKiToShI
                </p>
            </div>
        </div>
        """)
        text_browser.setOpenExternalLinks(True)
        text_browser.setReadOnly(True)
        layout.addWidget(text_browser)
        dialog.exec()


class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Нумерация строк
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginWidth(0, "0000")
        self.setMarginsForegroundColor(QColor(150, 150, 150))
        self.setMarginsBackgroundColor(QColor(60, 63, 65))

        # Подсветка синтаксиса
        lexer = QsciLexerPython()
        lexer.setColor(QColor(9, 145, 0), 1)    # Комментарии c #
        lexer.setColor(QColor(122, 191, 124), 2)   # Числа
        lexer.setColor(QColor(180, 90, 51), 3)    # Строки в кавычках c ""
        lexer.setColor(QColor(180, 90, 51), 4)   # Строки в кавычках c ''
        lexer.setColor(QColor(43, 150, 214), 5)   # Ключевые слова: def, class, if, else
        lexer.setColor(QColor(180, 90, 51), 6)   # Блочные комментарии c ''' '''
        lexer.setColor(QColor(205, 209, 100), 9)   # Название функций
        lexer.setColor(QColor(205, 209, 100), 15)  # Декораторы @staticmethod
        lexer.setColor(QColor(180, 90, 51), 17)  # f'{}'
        self.setSelectionBackgroundColor(QColor(0, 100, 200, 60))  # Выделение текста
        self.resetSelectionForegroundColor()
        self.setCaretForegroundColor(QColor(255, 255, 255))
        self.setCaretWidth(2)
        self.setLexer(lexer)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor(50, 50, 50))  # Подсветка строки


def main():
    app = QApplication(sys.argv)
    editor = TextEditor()
    editor.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
