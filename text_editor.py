from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QFileDialog,
                             QMessageBox, QListWidget, QDialog,
                             QTextBrowser, QVBoxLayout, QTableWidget,
                             QTableWidgetItem)
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from language import Language, LanguageDialog
from code_editor import CodeEditor
from PyQt6.QtGui import QAction
from PyQt6.uic import loadUi
import os
from ui_editor import Ui_MainWindow
from PyQt6.QtCore import QProcess
import re

# std::complex<double> my_complex(10.0, 2.0);
class TextEditor(QMainWindow, Ui_MainWindow):  # , Ui_MainWindow
    def __init__(self):
        super().__init__()
        # loadUi('text_editor.ui', self)
        self.setupUi(self)

        self.setMinimumSize(500, 400)

        self.lang = Language()
        self.apply_language()

        self.file_paths = {}
        self.input_to_output_map = {}
        self.status_bar = self.statusBar
        self.lexer_process = None
        self.current_input_widget = None
        self.current_tab_name = None

        self.setAcceptDrops(True)
        self.setup_actions()

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
            self.actionExit.triggered.connect(self.exit_app)

        # Run action
        self.actionRun = self.findChild(QAction, 'actionRun')
        if self.actionRun:
            self.actionRun.triggered.connect(self.run)

        # Edit actions
        self.actionUndo = self.findChild(QAction, 'actionUndo')
        if self.actionUndo:
            self.actionUndo.triggered.connect(self.undo)

        self.actionRedo = self.findChild(QAction, 'actionRedo')
        if self.actionRedo:
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

        # Help actions
        self.actionAbout = self.findChild(QAction, 'actionAbout')
        if self.actionAbout:
            self.actionAbout.triggered.connect(self.about)

        self.actionHelp = self.findChild(QAction, 'actionHelp')
        if self.actionHelp:
            self.actionHelp.triggered.connect(self.help)

        # Settings actions
        self.actionLanguage = self.findChild(QAction, 'actionLanguage')
        if self.actionLanguage:
            self.actionLanguage.triggered.connect(self.show_language_dialog)

        # Tabs
        self.input_tab_widget = self.findChild(QTabWidget, 'inputTabWidget')
        self.input_tab_widget.tabCloseRequested.connect(self.close_input_tab)

        self.output_tab_widget = self.findChild(QTabWidget, 'outputTabWidget')
        self.output_tab_widget.tabCloseRequested.connect(self.close_output_tab)

    def read_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        file_name = os.path.basename(file_path)
        return content, file_name

    def apply_language(self):
        t = self.lang.translations[self.lang.current_language]

        self.setWindowTitle(t['window_title'])

        self.menuFile.setTitle(t['menuFile'])
        self.menuEdit.setTitle(t['menuEdit'])
        self.menuText.setTitle(t['menuText'])
        self.menuRun.setTitle(t['menuRun'])
        self.menuHelp.setTitle(t['menuHelp'])
        self.menuSettings.setTitle(t['menuSettings'])

        action_names = [
            'actionNew', 'actionOpen', 'actionSave', 'actionSaveAs',
            'actionExit', 'actionUndo', 'actionRedo', 'actionCut',
            'actionCopy', 'actionPaste', 'actionDelete', 'actionSelectAll',
            'action_15', 'action_16', 'action_17', 'action_18', 'action_19',
            'action_20', 'action_21', 'actionRun', 'actionHelp',
            'actionAbout', 'actionLanguage'
        ]

        for action_name in action_names:
            action = getattr(self, action_name, None)
            if action:
                action.setText(t[action_name])

            tooltip_key = f"{action_name}_toolTip"
            if tooltip_key in t:
                action.setToolTip(t[tooltip_key])

        if hasattr(self, 'input_tab_widget') and self.input_tab_widget:
            for i in range(self.input_tab_widget.count()):
                widget = self.input_tab_widget.widget(i)
                if id(widget) not in self.file_paths:
                    self.input_tab_widget.setTabText(i, t['new_document'])

    def dragEnterEvent(self, event):
        if event is None or event.mimeData() is None:
            return

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.status_bar.showMessage(self.lang.translate('drop_hint'), 0)

    def dropEvent(self, event):
        if event is None or event.mimeData() is None:
            return

        opened = 0
        for url in event.mimeData().urls():
            if url.isLocalFile() and self.open_dropped_file(url.toLocalFile()):
                opened += 1

        self.status_bar.showMessage(
                self.lang.translate('opened_files').format(opened), 3000)

        event.acceptProposedAction()

    def open_dropped_file(self, file_path):
        return self.open_tab(file_path)

    def open_tab(self, file_path):
        try:
            content, file_name = self.read_file(file_path)
            self.create_new_tab(file_name, content, file_path)
            return True

        except Exception as e:
            QMessageBox.critical(self, self.lang.translate('error'),
                                 self.lang.translate('opening_error').
                                 format(str(e), 0),
                                 QMessageBox.StandardButton.Ok)
            return False

    def close_input_tab(self, index):
        widget = self.input_tab_widget.widget(index)
        tab_name = self.input_tab_widget.tabText(index)

        def closing():
            if id(widget) in self.file_paths:
                del self.file_paths[id(widget)]

            self.input_tab_widget.removeTab(index)
            widget.deleteLater()

        if widget.isModified():
            reply = QMessageBox.question(
                self,
                self.lang.translate('unsaved_changes'),
                self.lang.translate('save_changes').format(tab_name, 0),
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.input_tab_widget.setCurrentIndex(index)

                saved = self.save_file()

                if not saved:
                    self.status_bar.showMessage(
                        self.lang.translate('tab_closing_cancelled').format(tab_name, 0),
                        3000)
                    return

            elif reply == QMessageBox.StandardButton.No:
                closing()
                self.status_bar.showMessage(
                    self.lang.translate('tab_closed_without_saving').format(tab_name, 0),
                    3000)
                return

            elif reply == QMessageBox.StandardButton.Cancel:
                self.status_bar.showMessage(
                    self.lang.translate('tab_closing_cancelled').format(tab_name, 0),
                    3000)
                return

            self.status_bar.showMessage(self.lang.translate('tab_saved_and_closed').
                                        format(tab_name, 0), 3000)
        else:
            self.status_bar.showMessage(self.lang.translate('tab_closed').
                                        format(tab_name, 0), 3000)
        closing()

    def close_output_tab(self, index):
        widget = self.output_tab_widget.widget(index)
        tab_name = self.output_tab_widget.tabText(index)

        for input_widget, output_widget in list(self.input_to_output_map.items()):
            if output_widget == widget:
                del self.input_to_output_map[input_widget]
                break

        widget.deleteLater()
        self.output_tab_widget.removeTab(index)

        self.status_bar.showMessage(self.lang.translate('tab_closed').
                                    format(tab_name, 0), 3000)

    def can_close(self):
        for i in range(self.input_tab_widget.count()):
            widget = self.input_tab_widget.widget(i)
            if widget.isModified():
                tab_name = self.input_tab_widget.tabText(i)

                reply = QMessageBox.question(
                    self,
                    self.lang.translate('unsaved_changes'),
                    self.lang.translate('save_changes').format(tab_name),
                    QMessageBox.StandardButton.Yes |
                    QMessageBox.StandardButton.No |
                    QMessageBox.StandardButton.Cancel
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.input_tab_widget.setCurrentIndex(i)
                    if not self.save_file():
                        return False
                elif reply == QMessageBox.StandardButton.Cancel:
                    self.status_bar.showMessage(
                        self.lang.translate('tab_closing_cancelled').
                        format(tab_name),
                        3000)
                    return False

        return True

    def exit_app(self, event=None):
        self.close()

    def closeEvent(self, event):
        if self.can_close():
            event.accept()
        else:
            event.ignore()

    def open_file(self):
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self,
            self.lang.translate('choose_file_to_open'),
            "",
            "*.*"
        )

        if file_path:
            self.open_tab(file_path)

    def create_new_tab(self, title=None, content="", file_path=None):
        editor = CodeEditor()
        editor.setText(content)
        # editor.file_path = file_path

        if title is None:
            title = self.lang.translate('new_document')

        editor.setModified(False)

        index = self.input_tab_widget.addTab(editor, title)
        self.input_tab_widget.setCurrentIndex(index)

        if file_path:
            self.file_paths[id(editor)] = file_path
            self.status_bar.showMessage(self.lang.translate('file_opened').
                                        format(title, 0), 3000)
        else:
            self.status_bar.showMessage(f"{title}", 3000)

        return editor

    def new_file(self):
        self.create_new_tab()

    def save_file(self):
        widget = self.input_tab_widget.currentWidget()

        if not widget:
            return False

        file_path = self.file_paths.get(id(widget))

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(widget.text())

                widget.setModified(False)

                self.status_bar.showMessage(
                    self.lang.translate('file_saved').
                    format(os.path.basename(file_path)), 3000)

                return True

            except Exception as e:
                QMessageBox.critical(self, self.lang.translate('error'),
                                     self.lang.translate('file_saving_error').
                                     format(str(e)),
                                     QMessageBox.StandardButton.Ok)
                return False
        else:
            return self.save_file_as()

    def save_file_as(self):
        widget = self.input_tab_widget.currentWidget()

        if not widget:
            return False

        file_path, _ = QFileDialog.getSaveFileName(self,
                                                   self.lang.translate('actionSaveFileAs'),
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
                    file.write(widget.text())

                self.file_paths[id(widget)] = file_path

                widget.setModified(False)

                index = self.input_tab_widget.currentIndex()
                file_name = os.path.basename(file_path)
                self.input_tab_widget.setTabText(index, file_name)

                self.status_bar.showMessage(
                    self.lang.translate('file_saved_as').format(file_name, 0), 3000)
                return True

            except Exception as e:
                QMessageBox.critical(
                    self, self.lang.translate('error'),
                    self.lang.translate('file_saving_error').format(str(e), 0),
                    QMessageBox.StandardButton.Ok)
                return False
        else:
            self.status_bar.showMessage(self.lang.translate('save_cancelled'), 3000)
            return False

    def create_table(self, tokens_data):
        table = QTableWidget(self)

        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Условный код', 'Тип лексемы', 'Лексема', 'Местоположение'])

        rowLables = []
        if tokens_data:
            table.setRowCount(len(tokens_data))
            for row, token in enumerate(tokens_data):
                table.setItem(row, 0, QTableWidgetItem(str(token['code'])))
                table.setItem(row, 1, QTableWidgetItem(token['type']))
                table.setItem(row, 2, QTableWidgetItem(token['lexeme']))
                table.setItem(row, 3, QTableWidgetItem(token['location']))

                rowLables.append(f'Строка {token['line']}')
            table.setVerticalHeaderLabels(rowLables)
        else:
            table.setRowCount(0)

        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        return table

    def run(self):
        if not self.input_tab_widget:
            return

        self.save_file()
        index = self.input_tab_widget.currentIndex()
        self.current_input_widget = self.input_tab_widget.widget(index)
        self.current_tab_name = self.input_tab_widget.tabText(index)

        if self.current_input_widget in self.input_to_output_map:
            output_widget = self.input_to_output_map[self.current_input_widget]
            output_index = self.output_tab_widget.indexOf(output_widget)
            if output_index >= 0:
                self.output_tab_widget.setCurrentIndex(output_index)
                return
            else:
                del self.input_to_output_map[self.current_input_widget]

        text = self.current_input_widget.text()

        self.lexer_process = QProcess()
        self.lexer_process.readyReadStandardOutput.connect(self.on_lexer_output)
        self.lexer_process.readyReadStandardError.connect(self.on_lexer_error)
        self.lexer_process.finished.connect(self.on_lexer_finished)

        scanner_path = os.path.join('scanner', 'scanner.exe')
        self.lexer_process.start(scanner_path)

        self.lexer_process.write(text.encode('utf-8'))
        self.lexer_process.closeWriteChannel()

    def on_lexer_output(self):
        data = self.lexer_process.readAllStandardOutput()
        output = bytes(data).decode('utf-8')

        tokens = self.parse_lexer_output(output)
        table = self.create_table(tokens)

        self.output_table_data(table)

    def on_lexer_error(self):
        error_data = self.lexer_process.readAllStandardError()
        error = bytes(error_data).decode('utf-8')
        print(f"Ошибка лексера: {error}")

        table = self.create_table()
        table.setRowCount(1)
        table.setItem(0, 0, QTableWidgetItem("ERROR"))
        table.setItem(0, 1, QTableWidgetItem("Ошибка лексера"))
        table.setItem(0, 2, QTableWidgetItem(error[:50]))
        table.setItem(0, 3, QTableWidgetItem("-"))

        self.output_table_data(table)

    # [TODO] Сделать вывод в status_bar
    def on_lexer_finished(self, exit_code, exit_status):
        # print(f"Лексер завершен с кодом: {exit_code}")
        self.lexer_process = None

    def parse_lexer_output(self, output):
        tokens = []
        lines = output.strip().split('\n')

        # Парсим: "[1:1-3] - code=1: keyword int"
        pattern = r'\[(\d+):(\d+)-(\d+)\] - code=(\d+):\s*(.+)'

        for line in lines:
            if not line.strip():
                continue

            match = re.match(pattern, line)
            if match:
                line_num = match.group(1)
                start_col = match.group(2)
                end_col = match.group(3)
                code = match.group(4)
                description = match.group(5)

                token_type = self.get_token_type(int(code))

                if " " in description:
                    parts = description.split()
                    lexeme = parts[-1]

                tokens.append({
                    'line': line_num,
                    'code': code,
                    'type': token_type,
                    'lexeme': lexeme,
                    'location': f"{start_col}-{end_col}"
                })

        return tokens

    # [TODO] Сделать перевод
    def get_token_type(self, code):
        token_types = {
            1: "Ключевое слово int",
            2: "Ключевое слово float",
            3: "Ключевое слово double",
            4: "Ключевое слово std",
            5: "Ключевое слово complex",
            6: "Идентификатор",
            7: "Пробел",
            8: "Целое число",
            9: "Число с плавающей точкой",
            10: "Двойное двоеточие",
            11: "Открывающая угловая скобка",
            12: "Закрывающая угловая скобка",
            13: "Открывающая круглая скобка",
            14: "Закрывающая круглая скобка",
            15: "Минус",
            16: "Запятая",
            17: "Точка с запятой"
        }
        return token_types.get(code, f"Неизвестный код {code}")

    def output_table_data(self, table):
        self.output_tab_widget.addTab(table, self.current_tab_name)
        self.input_to_output_map[self.current_input_widget] = table
        self.output_tab_widget.setCurrentWidget(table)

    def undo(self):
        widget = self.get_current_input_tab_widget()
        if widget:
            widget.undo()
            self.status_bar.showMessage(self.lang.translate('actionUndo'), 3000)

    def redo(self):
        widget = self.get_current_input_tab_widget()
        if widget:
            widget.redo()
            self.status_bar.showMessage(self.lang.translate('actionRedo'), 3000)

    def copy(self):
        widget = self.get_current_input_tab_widget()
        if widget:
            if widget.hasSelectedText():
                widget.copy()
                self.status_bar.showMessage(self.lang.translate('actionCopy'), 3000)

    def paste(self):
        widget = self.get_current_input_tab_widget()
        if widget:
            widget.paste()
            self.status_bar.showMessage(self.lang.translate('actionPaste'), 3000)

    def cut(self):
        widget = self.get_current_input_tab_widget()
        if widget:
            if widget.hasSelectedText():
                widget.cut()
                self.status_bar.showMessage(self.lang.translate('actionCut'), 3000)

    def delete(self):
        widget = self.get_current_input_tab_widget()
        if widget:
            if widget.hasSelectedText():
                widget.removeSelectedText()
                self.status_bar.showMessage(self.lang.translate('actionDelete'), 3000)

    def select_all(self):
        widget = self.get_current_input_tab_widget()
        if widget:
            widget.selectAll()
            self.status_bar.showMessage(self.lang.translate('actionSelectAll'), 3000)

    def get_current_input_tab_widget(self):
        if hasattr(self, 'input_tab_widget') and self.input_tab_widget:
            current_widget = self.input_tab_widget.currentWidget()
            if isinstance(current_widget, CodeEditor):
                return current_widget
            else:
                self.status_bar.showMessage(self.lang.translate('text_edit_inactive'),
                                            3000)
                return None
        return None

    def show_language_dialog(self):
        dialog = LanguageDialog(self.lang, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_language = dialog.get_selected_language()

            if new_language != self.lang.current_language:
                self.lang.current_language = new_language
                self.lang.save_language_setting()
                self.apply_language()

                self.status_bar.showMessage(
                    self.lang.translate('language_changed'), 3000)
            else:
                self.status_bar.showMessage(
                    self.lang.translate('lang_not_changed'), 3000)
        else:
            self.status_bar.showMessage(
                self.lang.translate('lang_selection_cancelled'), 3000)

    def help(self):
        dialog = QDialog(self)

        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)

        dialog.setStyleSheet("background-color: #2b2b2b;")

        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()

        if self.lang.current_language == 'ru':
            dialog.setWindowTitle("Руководство пользователя")
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
                <div class='version'>Руководство пользователя | Версия 1.0.0</div>

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
                        <td><b>Выделить всё</b></td>
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

                <div style="text-align: center; font-size: 16px; font-weight: bold;">
                    <a href="https://github.com/MaKiToShI21/Text-Editor/blob/main/docs/ru/user_manual.md">Подробное руководство пользователя</a>
                </div>

                <div class='footer'>
                    <p>Разработано с использованием PyQt6</p>
                    <p>© 2026 MaKiToShI</p>
                </div>
            </body>
            </html>
            """)
        else:
            if self.lang.current_language == 'en':
                dialog.setWindowTitle("User manual")
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
                    <h1>Text editor</h1>
                    <div class='version'>User Manual | Version 1.0.0</div>

                    <h2 id='intro'>Introduction</h2>
                    <p><b>Text editor</b> — This application is for creating and editing text documents with parsing capabilities. The program provides a user-friendly interface for working with text and supports all basic editing operations.</p>

                    <h2 id='interface'>Program interface</h2>
                    <p>The main window of the text editor consists of the following elements:</p>
                    <ul>
                        <li><b>Window title</b> — displays the program name and the name of the current file</li>
                        <li><b>Main menu</b> — contains all available commands</li>
                        <li><b>Toolbar</b> — quick access buttons</li>
                        <li><b>Editing area</b> — a text field for entering and editing text</li>
                        <li><b>Results output area</b> — area for displaying the analyzer's results</li>
                        <li><b>Status bar</b> — displays information about the application's running status</li>
                    </ul>

                    <h2 id='file-menu'>Menu «File»</h2>
                    <table>
                        <tr>
                            <th>Command</th>
                            <th>Hotkey</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <td><b>Create</b></td>
                            <td><span>Ctrl+N</span=></td>
                            <td>Creates a new document in a new tab.</td>
                        </tr>
                        <tr>
                            <td><b>Open</b></td>
                            <td><span>Ctrl+O</span></td>
                            <td>Opens an existing text file.</td>
                        </tr>
                        <tr>
                            <td><b>Save</b></td>
                            <td><span>Ctrl+S</span></td>
                            <td>Saves the current document</td>
                        </tr>
                        <tr>
                            <td><b>Save as</b></td>
                            <td><span>Ctrl+Shift+S</span></td>
                            <td>Saves the document under a new name</td>
                        </tr>
                        <tr>
                            <td><b>Exit</b></td>
                            <td><span>Ctrl+Q</span></td>
                            <td>Terminates the program</td>
                        </tr>
                    </table>

                    <p>When you try to close an unsaved document, the program will prompt you to save changes.</p>

                    <h2 id='edit-menu'>Menu «Edit»</h2>
                    <table>
                        <tr>
                            <th>Command</th>
                            <th>Hotkey</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <td><b>Undo</b></td>
                            <td><span>Ctrl+Z</span></td>
                            <td>Undoes the last action</td>
                        </tr>
                        <tr>
                            <td><b>Redo</b></td>
                            <td><span>Ctrl+Y</span></td>
                            <td>Redoes the undone action</td>
                        </tr>
                        <tr>
                            <td><b>Cut</b></td>
                            <td><span>Ctrl+X</span></td>
                            <td>Copies the selected text to the clipboard and deletes it.</td>
                        </tr>
                        <tr>
                            <td><b>Copy</b></td>
                            <td><span>Ctrl+C</span></td>
                            <td>Copies the selected text to the clipboard</td>
                        </tr>
                        <tr>
                            <td><b>Paste</b></td>
                            <td><span>Ctrl+V</span></td>
                            <td>Pastes text from the clipboard</td>
                        </tr>
                        <tr>
                            <td><b>Delete</b></td>
                            <td><span>Del</span></td>
                            <td>Deletes the selected text</td>
                        </tr>
                        <tr>
                            <td><b>Select all</b></td>
                            <td><span>Ctrl+A</span></td>
                            <td>Selects all text in a document</td>
                        </tr>
                    </table>

                    <h2 id='text-menu'>Menu «Text»</h2>
                    <p>Menu «Text» contains information sections on language and grammar:</p>
                    <ul>
                        <li><b>Statement of the problem</b> — description of the purpose and objectives of the work</li>
                        <li><b>Grammar</b> — formal description of the grammar of a language</li>
                        <li><b>Classification of grammar</b> — Chomsky's type of grammar</li>
                        <li><b>Method of analysis</b> — description of the syntactic analysis method</li>
                        <li><b>Test example</b> — example of parsing an input string</li>
                        <li><b>Bibliography</b> — sources used</li>
                        <li><b>Source code of the program</b> — program code</li>
                    </ul>
                    <p>When you select any item, a window with the corresponding information opens.</p>

                    <h2 id='run-menu'>Menu «Run»</h2>
                    <p><b>Launching the analyzer</b> (<span>F5</span>) — starts parsing the text from the editing area.</p>

                    <p><b>Results of the analysis:</b></p>
                    <ul>
                        <li>Erroneous lines are marked in red with the position of the error indicated.</li>
                        <li>Clicking on an error message moves the cursor to the erroneous section</li>
                    </ul>

                    <h2 id='help-menu'>Menu «Help»</h2>
                    <table>
                        <tr>
                            <th>Command</th>
                            <th>Hotkey</th>
                            <th>Description</th>
                        </tr>
                        <tr>
                            <td><b>Call for help</b></td>
                            <td><span>F1</span></td>
                            <td>Opens this user guide</td>
                        </tr>
                        <tr>
                            <td><b>About the program</b></td>
                            <td>F2</td>
                            <td>Information about the program and the developer</td>
                        </tr>
                    </table>

                    <h2>Working with editing and output areas</h2>
                    <p><b>Editing area:</b> designed for entering and editing text. All standard editing operations are supported.</p>
                    <p><b>Results output area:</b> Displays the results of the parser. This area is read-only.</p>
                    <p><b>Resizing areas:</b> drag the divider between areas with the mouse.</p>

                    <div style="text-align: center; font-size: 16px; font-weight: bold;">
                        <a href="https://github.com/MaKiToShI21/Text-Editor/blob/main/docs/en/user_manual.md">Detailed user manual</a>
                    </div>

                    <div class='footer'>
                        <p>Developed using PyQt6</p>
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
        dialog.setMinimumWidth(450)
        dialog.setMinimumHeight(300)
        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        if self.lang.current_language == 'ru':
            dialog.setWindowTitle("О программе")
            text_browser.setHtml("""
                <div style='text-align: center;'>
                    <h1>Текстовый редактор</h1>
                    <p style='color: #868e94; font-size: 14px;'>Версия 1.0.0</p>

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
        else:
            dialog.setWindowTitle("About the program")
            text_browser.setHtml("""
                <div style='text-align: center;'>
                    <h1>Text editor</h1>
                    <p style='color: #868e94; font-size: 14px;'>Version 1.0.0</p>

                    <div style='padding: 5px;'>
                        <p style='font-size: 16px; line-height: 1;'>
                            A program for editing text files with syntax analysis capabilities
                        </p>
                    </div>

                    <div>
                        <p><b>Developer:</b> MaKiToShI</p>
                        <p><b>Год:</b> 2026</p>
                    </div>

                    <div style='border-top: 1px solid #dee2e6; padding-top: 15px;'>
                        <p style='color: #868e94; font-size: 12px;'>
                            Developed using PyQt6<br>
                            © 2026 MaKiToShI
                        </p>
                    </div>
                </div>
                """)

        text_browser.setOpenExternalLinks(True)
        text_browser.setReadOnly(True)
        layout.addWidget(text_browser)
        dialog.exec()
