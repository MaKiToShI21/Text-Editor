from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QFileDialog,
                             QMessageBox, QListWidget, QDialog,
                             QTextBrowser, QVBoxLayout, QTableWidget,
                             QTableWidgetItem)
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from language import Language, LanguageDialog
from ui_editor import Ui_MainWindow
from code_editor import CodeEditor
from PyQt6.QtCore import QProcess
from lexer import LexicalAnalyzer
from PyQt6.QtGui import QAction
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
import re
import os
import sys
import os
import tempfile
import shutil


# std::complex<double> my_complex(10.0, 2.0);
class TextEditor(QMainWindow, Ui_MainWindow):  # , Ui_MainWindow
    def __init__(self):
        super().__init__()
        # loadUi('text_editor.ui', self)
        self.setupUi(self)

        self.setMinimumSize(500, 400)

        self.lang = Language()
        self.apply_language()

        self.input_to_output_map = {}
        self.status_bar = self.statusBar
        self.lexer_process = None
        self.current_input_widget = None
        self.current_tab_name = None
        self.current_file_path = None
        self.my_lexer = False

        self.setAcceptDrops(True)
        self.setup_actions()

    def setup_actions(self):
        action_map = {
            'actionOpen': self.open_file,
            'actionNew': self.new_file,
            'actionSave': self.save_file,
            'actionSaveAs': self.save_file_as,
            'actionExit': self.exit_app,
            'actionRun': self.run,
            'actionHelp': self.help,
            'actionAbout': self.about,
            'actionLanguage': self.show_language_dialog
        }

        for name, method in action_map.items():
            action = self.findChild(QAction, name)
            if action:
                action.triggered.connect(method)

        # Edit actions
        edit_methods = {
            'actionUndo': 'undo', 'actionRedo': 'redo',
            'actionCut': 'cut', 'actionCopy': 'copy',
            'actionPaste': 'paste', 'actionDelete': 'removeSelectedText',
            'actionSelectAll': 'selectAll'
        }

        for action_name, method_name in edit_methods.items():
            action = self.findChild(QAction, action_name)
            if action:
                action.triggered.connect(
                    lambda checked, an=action_name, mn=method_name: 
                    self.edit_action(an, mn)
                )

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
                if not hasattr(widget, 'file_path') or not widget.file_path:
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
                                 format(str(e), 0))
            return False

    def close_input_tab(self, index):
        widget = self.input_tab_widget.widget(index)
        tab_name = self.input_tab_widget.tabText(index)
        file_path = getattr(widget, 'file_path', None)

        def closing():
            if file_path and file_path in self.input_to_output_map:
                output_widget = self.input_to_output_map[file_path]
                output_index = self.output_tab_widget.indexOf(output_widget)
                if output_index >= 0:
                    self.output_tab_widget.removeTab(output_index)
                    output_widget.deleteLater()
                del self.input_to_output_map[file_path]
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

        for file_path, output_widget in list(self.input_to_output_map.items()):
            if output_widget == widget:
                del self.input_to_output_map[file_path]
                break

        widget.deleteLater()
        self.output_tab_widget.removeTab(index)
        self.status_bar.showMessage(self.lang.translate('tab_closed').
                                    format(tab_name, 0), 3000)

    def can_close(self):
        for i in range(self.input_tab_widget.count()):
            widget = self.input_tab_widget.widget(i)
            if not widget.isModified():
                continue
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
        self.cleanup_temp_files()
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
        editor.file_path = file_path

        if title is None:
            title = self.lang.translate('new_document')

        editor.setModified(False)

        index = self.input_tab_widget.addTab(editor, title)
        self.input_tab_widget.setCurrentIndex(index)

        if file_path:
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

        file_path = getattr(widget, 'file_path', None)
        if not file_path:
            return self.save_file_as()

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(widget.text())
            widget.file_path = file_path
            widget.setModified(False)
            self.status_bar.showMessage(
                self.lang.translate('file_saved').
                format(os.path.basename(file_path)), 3000)
            return True
        except Exception as e:
            QMessageBox.critical(self, self.lang.translate('error'),
                                 self.lang.translate('file_saving_error').
                                 format(str(e)))
            return False

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

        if not file_path:
            self.status_bar.showMessage(self.lang.translate('save_cancelled'), 3000)
            return False

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(widget.text())

            widget.file_path = file_path

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

    def get_lexer_path(self):
        if getattr(sys, 'frozen', False):
            # app_dir = os.path.dirname(sys.executable)
            # external_lexer = os.path.join(app_dir, 'lexer', 'lexer.exe')

            # if os.path.exists(external_lexer):
            #     return external_lexer

            return self.extract_lexer_from_resources()
        else:
            return os.path.join(os.path.dirname(__file__), 'lexer', 'lexer.exe')

    def extract_lexer_from_resources(self):
        try:
            if hasattr(self, 'temp_lexer_path') and self.temp_lexer_path:
                if os.path.exists(self.temp_lexer_path):
                    return self.temp_lexer_path

            source = os.path.join(sys._MEIPASS, 'lexer', 'lexer.exe')

            if not os.path.exists(source):
                return None

            temp_dir = tempfile.mkdtemp(prefix='texteditor_')
            temp_path = os.path.join(temp_dir, 'lexer.exe')

            shutil.copy2(source, temp_path)

            self.temp_lexer_path = temp_path
            self.temp_lexer_dir = temp_dir

            return temp_path
        except Exception as e:
            return None

    def cleanup_temp_files(self):
        if hasattr(self, 'temp_lexer_path') and self.temp_lexer_path:
            try:
                if os.path.exists(self.temp_lexer_path):
                    os.remove(self.temp_lexer_path)
                if hasattr(self, 'temp_lexer_dir') and os.path.exists(self.temp_lexer_dir):
                    os.rmdir(self.temp_lexer_dir)
            except:
                pass

    # def run(self):
    #     if not self.input_tab_widget:
    #         return
    #     index = self.input_tab_widget.currentIndex()
    #     self.current_input_widget = self.input_tab_widget.widget(index)
    #     self.current_file_path = self.current_input_widget.file_path

    #     if not self.current_file_path or self.current_input_widget.isModified():
    #         if not self.save_file():
    #             return
    #         if self.current_input_widget.file_path:
    #             self.current_file_path = self.current_input_widget.file_path

    #     self.current_tab_name = self.input_tab_widget.tabText(index)

    #     if self.current_file_path in self.input_to_output_map:
    #         output_widget = self.input_to_output_map[self.current_file_path]
    #         output_index = self.output_tab_widget.indexOf(output_widget)
    #         self.output_tab_widget.setCurrentIndex(output_index)

    #     text = self.current_input_widget.text()

    #     if self.my_lexer:
    #         lexer = LexicalAnalyzer(self.lang)
    #         tokens, errors = lexer.analyze(text)
    #         self.create_or_update_table(tokens, errors)
    #     else:
    #         lexer_path = self.get_lexer_path()

    #         self.lexer_process = QProcess()
    #         self.lexer_process.readyReadStandardOutput.connect(self.on_lexer_output)
    #         self.lexer_process.readyReadStandardError.connect(self.on_lexer_error)
    #         self.lexer_process.finished.connect(self.on_lexer_finished)

    #         self.lexer_process.start(lexer_path)
    #         self.lexer_process.write(text.encode('utf-8'))
    #         self.lexer_process.closeWriteChannel()

    def on_lexer_output(self):
        data = self.lexer_process.readAllStandardOutput()

        try:
            output = bytes(data).decode('cp1251')
        except:
            try:
                output = bytes(data).decode('utf-8')
            except:
                output = bytes(data).decode('cp866', errors='replace')

        tokens, errors = self.parse_lexer_output(output)
        self.create_or_update_table(tokens, errors)

    def on_lexer_error(self):
        error_data = self.lexer_process.readAllStandardError()
        error = bytes(error_data).decode('utf-8')
        table = self.create_or_update_table(None)
        table.setRowCount(1)
        table.setItem(0, 0, QTableWidgetItem("ERROR"))
        table.setItem(0, 1, QTableWidgetItem("Lexer error"))
        table.setItem(0, 2, QTableWidgetItem(error[:50]))
        table.setItem(0, 3, QTableWidgetItem(""))

        self.output_table_data(table)

    def on_lexer_finished(self, exit_code, exit_status):
        self.lexer_process = None

    def parse_lexer_output(self, output):
        tokens = []
        errors = []
        lines = output.strip().split('\n')

        # Парсим: "[1:1-3] - code=1: keyword int"
        pattern = r'\[(\d+):(\d+)-(\d+)\] - code=(\d+):\s*(.+)'
        error_pattern = r'\[(\d+):(\d+)-(\d+)\] - ERROR:\s*(.+)'

        # Для объединения смежных ошибок
        current_error = None
        prev_end_col = None
        prev_line_num = None

        for line in lines:
            if not line.strip():
                continue

            error_match = re.match(error_pattern, line)
            if error_match:
                line_num = int(error_match.group(1))
                start_col = int(error_match.group(2))
                end_col = int(error_match.group(3))
                error_msg = error_match.group(4)

                parts = error_msg.split(' ')
                lexeme = parts[-1] if " " in error_msg else error_msg

                # Проверяем, является ли текущая ошибка продолжением предыдущей
                if (current_error and 
                    prev_line_num == line_num and 
                    prev_end_col and 
                    prev_end_col + 1 == start_col):
                    # Объединяем с предыдущей ошибкой
                    current_error['lexeme'] += lexeme
                    current_error['location'] = f"{self.lang.translate('line_num').format(line_num, 0)}, {current_error['start_col']}-{end_col}"
                else:
                    # Если была предыдущая ошибка, добавляем её в список
                    if current_error:
                        # Удаляем временные поля
                        del current_error['start_col']
                        errors.append(current_error)

                    # Создаём новую ошибку
                    current_error = {
                        'code': 'ERROR',
                        'type': self.lang.translate('invalid_char'),
                        'lexeme': lexeme,
                        'start_col': start_col,
                        'location': f"{self.lang.translate('line_num').format(line_num, 0)}, {start_col}-{end_col}",
                    }

                prev_end_col = end_col
                prev_line_num = line_num
                continue

            # Если встретили обычный токен, добавляем накопленную ошибку
            if current_error:
                del current_error['start_col']
                errors.append(current_error)
                current_error = None
                prev_end_col = None
                prev_line_num = None

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
                elif description == 'space':
                    lexeme = ' '
                else:
                    lexeme = description

                tokens.append({
                    'code': code,
                    'type': token_type,
                    'lexeme': lexeme,
                    'location': f"{self.lang.translate('line_num').format(line_num, 0)}, {start_col}-{end_col}",
                })

        # Добавляем последнюю накопленную ошибку
        if current_error:
            del current_error['start_col']
            errors.append(current_error)

        return tokens, errors

    # def parse_lexer_output(self, output):
        tokens = []
        errors = []
        lines = output.strip().split('\n')

        # Парсим: "[1:1-3] - code=1: keyword int"
        pattern = r'\[(\d+):(\d+)-(\d+)\] - code=(\d+):\s*(.+)'
        error_pattern = r'\[(\d+):(\d+)-(\d+)\] - ERROR:\s*(.+)'

        for line in lines:
            if not line.strip():
                continue

            error_match = re.match(error_pattern, line)
            if error_match:
                line_num = error_match.group(1)
                start_col = error_match.group(2)
                end_col = error_match.group(3)
                error_msg = error_match.group(4)

                if " " in error_msg:
                    parts = error_msg.split(' ')

                errors.append({
                    'code': 'ERROR',
                    'type': self.lang.translate('invalid_char'),
                    'lexeme': parts[-1],
                    'location': f"{self.lang.translate('line_num').format(line_num, 0)}, {start_col}-{end_col}",
                })
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
                elif description == 'space':
                    lexeme = ' '
                else:
                    lexeme = description

                tokens.append({
                    'code': code,
                    'type': token_type,
                    'lexeme': lexeme,
                    'location': f"{self.lang.translate('line_num').format(line_num, 0)}, {start_col}-{end_col}",
                })

        return tokens, errors

    def get_token_type(self, code):
        lexer = LexicalAnalyzer(self.lang)
        return lexer.TOKEN_TYPES.get(code, self.lang.translate('unknown_code').format(code, 0))

    def create_or_update_table(self, tokens, errors):
        existing_table = self.input_to_output_map.get(self.current_file_path)

        if existing_table and self.output_tab_widget.indexOf(existing_table) >= 0:
            self.fill_table(tokens, errors, existing_table)
            self.output_tab_widget.setCurrentWidget(existing_table)
        else:
            table = self.fill_table(tokens, errors)
            self.output_table_data(table)

    def fill_table(self, tokens, errors, table=None):
        if table:
            table.clearContents()
            table.setRowCount(0)
        else:
            table = QTableWidget(self)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            self.lang.translate('cond_code'),
            self.lang.translate('lexeme_type'),
            self.lang.translate('lexeme'),
            self.lang.translate('location')])

        if tokens:
            total_rows = len(tokens) + len(errors)
            table.setRowCount(total_rows)
            rowLables = []
            for row, token in enumerate(tokens):
                table.setItem(row, 0, QTableWidgetItem(str(token['code'])))
                table.setItem(row, 1, QTableWidgetItem(token['type']))
                table.setItem(row, 2, QTableWidgetItem(token['lexeme']))
                table.setItem(row, 3, QTableWidgetItem(token['location']))
                rowLables.append(str(row + 1))
            if errors:
                for i, error in enumerate(errors):
                    row = len(tokens) + i
                    item_code = QTableWidgetItem(error['code'])
                    item_code.setForeground(Qt.GlobalColor.red)
                    table.setItem(row, 0, item_code)

                    item_type = QTableWidgetItem(error['type'])
                    item_type.setForeground(Qt.GlobalColor.red)
                    table.setItem(row, 1, item_type)

                    item_lexeme = QTableWidgetItem(error['lexeme'])
                    item_lexeme.setForeground(Qt.GlobalColor.red)
                    table.setItem(row, 2, item_lexeme)

                    item_loc = QTableWidgetItem(error['location'])
                    item_loc.setForeground(Qt.GlobalColor.red)
                    table.setItem(row, 3, item_loc)

                    rowLables.append(str(row + 1))
            table.itemClicked.connect(self.on_table_item_clicked)
        else:
            table.setRowCount(0)

        table.setVerticalHeaderLabels(rowLables)
        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        return table

    def on_table_item_clicked(self, item):
        row = item.row()
        table = item.tableWidget()

        location_text = table.item(row, 3).text()

        match = re.match(r'.*?(\d+),\s*(\d+)-(\d+)', location_text)
        if match:
            line_num = int(match.group(1))
            start_col = int(match.group(2))
            end_col = int(match.group(3))

            editor = self.input_tab_widget.currentWidget()
            if editor:
                line_start_pos = editor.SendScintilla(editor.SCI_POSITIONFROMLINE, line_num - 1)
                start_pos = line_start_pos + start_col - 1
                end_pos = line_start_pos + end_col

                editor.SendScintilla(editor.SCI_SETSEL, start_pos, end_pos)
                editor.SendScintilla(editor.SCI_SCROLLCARET)

    def output_table_data(self, table):
        self.output_tab_widget.addTab(table, self.current_tab_name)
        self.input_to_output_map[self.current_file_path] = table
        self.output_tab_widget.setCurrentWidget(table)

    def edit_action(self, action_name, method_name):
        widget = self.get_current_input_tab_widget()
        if widget:
            getattr(widget, method_name)()
            self.status_bar.showMessage(self.lang.translate(action_name), 3000)

    def get_current_input_tab_widget(self):
        if not self.input_tab_widget:
            return None
        widget = self.input_tab_widget.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        else:
            self.status_bar.showMessage(self.lang.
                                        translate('text_edit_inactive'), 3000)
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

    def run(self):
        if not self.input_tab_widget:
            return
        index = self.input_tab_widget.currentIndex()
        self.current_input_widget = self.input_tab_widget.widget(index)
        self.current_file_path = self.current_input_widget.file_path

        if not self.current_file_path or self.current_input_widget.isModified():
            if not self.save_file():
                return
            if self.current_input_widget.file_path:
                self.current_file_path = self.current_input_widget.file_path

        self.current_tab_name = self.input_tab_widget.tabText(index)

        if self.current_file_path in self.input_to_output_map:
            output_widget = self.input_to_output_map[self.current_file_path]
            output_index = self.output_tab_widget.indexOf(output_widget)
            self.output_tab_widget.setCurrentIndex(output_index)

        text = self.current_input_widget.text()

        xml_comment_regex = r'<!--(.*?)-->'

        matches = []
        pattern = re.compile(xml_comment_regex, re.DOTALL)

        for match in pattern.finditer(text):
            comment_text = match.group(1).strip()
            start_pos = match.start()
            end_pos = match.end()
            length = end_pos - start_pos
            substring = f"<!--{comment_text}-->"

            line_num = text.count('\n', 0, start_pos) + 1
            line_start = text.rfind('\n', 0, start_pos) + 1
            start_col = start_pos - line_start + 1
            end_line_num = text.count('\n', 0, end_pos) + 1

            if line_num == end_line_num:
                end_col = end_pos - line_start
                location = f"{line_num}, {start_col}-{end_col}"
            else:
                location = f"{line_num}, {start_col}-{start_col + length}"

            matches.append({
                'substring': substring,
                'location': location,
                'length': length,
                'start_pos': start_pos,
                'end_pos': end_pos,
                'line_num': line_num,
                'start_col': start_col
            })

        self.create_comment_table(matches, self.current_file_path)

    def create_comment_table(self, matches, file_path):
        if file_path and file_path in self.input_to_output_map:
            old_table = self.input_to_output_map[file_path]
            index = self.output_tab_widget.indexOf(old_table)
            if index >= 0:
                self.output_tab_widget.removeTab(index)
                old_table.deleteLater()
            del self.input_to_output_map[file_path]

        table = QTableWidget()
        table.setColumnCount(3)

        if self.lang.current_language == 'ru':
            headers = ['Найденная подстрока', 'Позиция', 'Длина']
        else:
            headers = ['Found substring', 'Position', 'Length']
        table.setHorizontalHeaderLabels(headers)

        if not matches:
            table.setRowCount(0)
        else:
            table.setRowCount(len(matches))

            for row, match in enumerate(matches):
                substring_item = QTableWidgetItem(match['substring'])
                substring_item.setToolTip(f"XML comment: {match['substring']}")
                table.setItem(row, 0, substring_item)

                location_item = QTableWidgetItem(match['location'])
                table.setItem(row, 1, location_item)

                length_item = QTableWidgetItem(str(match['length']))
                length_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                table.setItem(row, 2, length_item)

            table.matches_data = matches

        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.resizeColumnsToContents()

        table.itemClicked.connect(self.on_comment_table_clicked)

        tab_name = self.input_tab_widget.tabText(self.input_tab_widget.currentIndex())
        tab_display_name = f"{tab_name}"

        self.output_tab_widget.addTab(table, tab_display_name)
        if file_path:
            self.input_to_output_map[file_path] = table
        self.output_tab_widget.setCurrentWidget(table)

        table.setColumnWidth(0, 500)
        table.setColumnWidth(1, 200)
        table.setColumnWidth(2, 80)

    def on_comment_table_clicked(self, item):
        row = item.row()
        table = item.tableWidget()

        if not hasattr(table, 'matches_data') or row >= len(table.matches_data):
            return

        match = table.matches_data[row]

        editor = self.input_tab_widget.currentWidget()
        if not editor:
            return

        start_pos = match['start_pos']
        end_pos = match['end_pos']

        try:
            editor.SendScintilla(editor.SCI_SETSEL, start_pos, end_pos)
            editor.SendScintilla(editor.SCI_SCROLLCARET)
            editor.setFocus()
        except AttributeError:
            cursor = editor.textCursor()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, cursor.MoveMode.KeepAnchor)
            editor.setTextCursor(cursor)
            editor.setFocus()
