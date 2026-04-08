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
from my_parser import MyParser
from cs_parser import Parser as RecursiveParser
from avt_parser import Parser as AutomaticParser
from PyQt6.QtGui import QAction
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
import re
import os
import sys
import os
import tempfile
import shutil

# std::complex<double> my_complex(-10.0, 2.0);
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
        self.my_lexer = True
        self.my_parser = False

        self.setAcceptDrops(True)
        self.setup_actions()

    def setup_actions(self):
        action_map = {
            'actionOpen': self.open_file,
            'actionNew': self.new_file,
            'actionSave': self.save_file,
            'actionSaveAs': self.save_file_as,
            'actionExit': self.exit_app,
            'actionRunLexer': self.runLexer,
            'actionRunParser': self.runParser,
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
            'action_20', 'action_21', 'actionRunParser', 'actionRunLexer', 'actionHelp',
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
                                                   "РўРµРєСЃС‚РѕРІС‹Рµ С„Р°Р№Р»С‹ (*.txt);;"
                                                   "doc (*.doc);;"
                                                   "docx (*.docx);;"
                                                   "PDF (*.pdf);;"
                                                   "rtf (*.rtf);;"
                                                   "Р’СЃРµ С„Р°Р№Р»С‹ (*.*)")

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

    def runLexer(self):
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

        if self.my_lexer:
            lexer = LexicalAnalyzer(self.lang)
            tokens, errors = lexer.analyze(text)
            self.create_or_update_table(tokens, errors)
        else:
            lexer_path = self.get_lexer_path()

            self.lexer_process = QProcess()
            self.lexer_process.readyReadStandardOutput.connect(self.on_lexer_output)
            self.lexer_process.readyReadStandardError.connect(self.on_lexer_error)
            self.lexer_process.finished.connect(self.on_lexer_finished)

            self.lexer_process.start(lexer_path)
            self.lexer_process.write(text.encode('utf-8'))
            self.lexer_process.closeWriteChannel()

    def runParser(self):
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

        if self.my_parser:
            parser = MyParser(self.lang)
            _, errors = parser.parse(text)
        else:
            # parser = RecursiveParser(self.lang)
            # parser.parse_complex_declaration(text)
            # errors = parser.errors
            parser = AutomaticParser(self.lang)
            _, errors = parser.parse(text)

        self.create_or_update_parser_table(errors)
        self.status_bar.showMessage(self.lang.translate('total_errors').format(len(errors), 0))

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

        # РџР°СЂСЃРёРј: "[1:1-3] - code=1: keyword int"
        pattern = r'\[(\d+):(\d+)-(\d+)\] - code=(\d+):\s*(.+)'
        error_pattern = r'\[(\d+):(\d+)-(\d+)\] - ERROR:\s*(.+)'

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

                if (current_error and
                    prev_line_num == line_num and
                    prev_end_col and
                    prev_end_col + 1 == start_col):
                    current_error['lexeme'] += lexeme
                    current_error['location'] = f"{self.lang.translate('line_num').format(line_num, 0)}, {current_error['start_col']}-{end_col}"
                else:
                    if current_error:
                        del current_error['start_col']
                        errors.append(current_error)

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

        if current_error:
            del current_error['start_col']
            errors.append(current_error)

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

                    rowLables.append(str(row))
            self._rebind_table_click_handler(table, self.on_table_item_clicked)
        else:
            table.setRowCount(0)

        table.setVerticalHeaderLabels(rowLables)
        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        return table

    def create_or_update_parser_table(self, errors):
        existing_table = self.input_to_output_map.get(self.current_file_path)

        if existing_table and self.output_tab_widget.indexOf(existing_table) >= 0:
            self.fill_parser_table(errors, existing_table)
            self.output_tab_widget.setCurrentWidget(existing_table)
        else:
            table = self.fill_parser_table(errors)
            self.output_table_data(table)

    def fill_parser_table(self, errors, table=None):
        if table:
            table.clearContents()
            table.setRowCount(0)
        else:
            table = QTableWidget(self)

        table.setColumnCount(3)
        table.setHorizontalHeaderLabels([
            "Неверный фрагмент",
            "Описание ошибки",
            self.lang.translate('location'),
        ])

        row_labels = []
        if errors:
            table.setRowCount(len(errors))
            for row, error in enumerate(errors):
                fragment = QTableWidgetItem(error.get('lexeme', ''))
                fragment.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 0, fragment)

                description_text = error.get('description', error.get('type', ''))
                description = QTableWidgetItem(description_text)
                description.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 1, description)

                location = QTableWidgetItem(error.get('location', ''))
                location.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 2, location)

                row_labels.append(str(row + 1))
            self._rebind_table_click_handler(table, self.on_parser_table_item_clicked)
        else:
            table.setRowCount(0)

        table.setVerticalHeaderLabels(row_labels)
        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return table

    def on_parser_table_item_clicked(self, item):
        row = item.row()
        table = item.tableWidget()

        location_item = self._get_location_item(table, row, fallback_col=2)
        if not location_item:
            return
        self._highlight_location(location_item.text())

    def on_table_item_clicked(self, item):
        row = item.row()
        table = item.tableWidget()

        location_item = self._get_location_item(table, row, fallback_col=3)
        if not location_item:
            return
        self._highlight_location(location_item.text())

    def _highlight_location(self, location_text):
        match = re.match(r'.*?(\d+),\s*(\d+)-(\d+)', location_text or '')
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

    def _get_location_item(self, table, row, fallback_col):
        location_col = self._get_location_column_index(table, fallback_col)
        if location_col is None:
            return None
        return table.item(row, location_col)

    def _get_location_column_index(self, table, fallback_col):
        if table is None:
            return None
        location_header = self.lang.translate('location')
        for col in range(table.columnCount()):
            header_item = table.horizontalHeaderItem(col)
            if header_item and header_item.text() == location_header:
                return col
        if 0 <= fallback_col < table.columnCount():
            return fallback_col
        return None

    @staticmethod
    def _rebind_table_click_handler(table, handler):
        if table is None:
            return
        try:
            table.itemClicked.disconnect()
        except Exception:
            pass
        table.itemClicked.connect(handler)
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
            dialog.setWindowTitle("Р СѓРєРѕРІРѕРґСЃС‚РІРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ")
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
                <h1>РўРµРєСЃС‚РѕРІС‹Р№ СЂРµРґР°РєС‚РѕСЂ</h1>
                <div class='version'>Р СѓРєРѕРІРѕРґСЃС‚РІРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ | Р’РµСЂСЃРёСЏ 1.0.0</div>

                <h2 id='intro'>Р’РІРµРґРµРЅРёРµ</h2>
                <p><b>РўРµРєСЃС‚РѕРІС‹Р№ СЂРµРґР°РєС‚РѕСЂ</b> вЂ” СЌС‚Рѕ РїСЂРёР»РѕР¶РµРЅРёРµ РґР»СЏ СЃРѕР·РґР°РЅРёСЏ Рё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ С‚РµРєСЃС‚РѕРІС‹С… РґРѕРєСѓРјРµРЅС‚РѕРІ СЃ РІРѕР·РјРѕР¶РЅРѕСЃС‚СЊСЋ СЃРёРЅС‚Р°РєСЃРёС‡РµСЃРєРѕРіРѕ Р°РЅР°Р»РёР·Р°. РџСЂРѕРіСЂР°РјРјР° РїСЂРµРґРѕСЃС‚Р°РІР»СЏРµС‚ СѓРґРѕР±РЅС‹Р№ РёРЅС‚РµСЂС„РµР№СЃ РґР»СЏ СЂР°Р±РѕС‚С‹ СЃ С‚РµРєСЃС‚РѕРј Рё РїРѕРґРґРµСЂР¶РёРІР°РµС‚ РІСЃРµ РѕСЃРЅРѕРІРЅС‹Рµ РѕРїРµСЂР°С†РёРё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ.</p>

                <h2 id='interface'>РРЅС‚РµСЂС„РµР№СЃ РїСЂРѕРіСЂР°РјРјС‹</h2>
                <p>Р“Р»Р°РІРЅРѕРµ РѕРєРЅРѕ С‚РµРєСЃС‚РѕРІРѕРіРѕ СЂРµРґР°РєС‚РѕСЂР° СЃРѕСЃС‚РѕРёС‚ РёР· СЃР»РµРґСѓСЋС‰РёС… СЌР»РµРјРµРЅС‚РѕРІ:</p>
                <ul>
                    <li><b>Р—Р°РіРѕР»РѕРІРѕРє РѕРєРЅР°</b> вЂ” РѕС‚РѕР±СЂР°Р¶Р°РµС‚ РЅР°Р·РІР°РЅРёРµ РїСЂРѕРіСЂР°РјРјС‹ Рё РёРјСЏ С‚РµРєСѓС‰РµРіРѕ С„Р°Р№Р»Р°</li>
                    <li><b>Р“Р»Р°РІРЅРѕРµ РјРµРЅСЋ</b> вЂ” СЃРѕРґРµСЂР¶РёС‚ РІСЃРµ РґРѕСЃС‚СѓРїРЅС‹Рµ РєРѕРјР°РЅРґС‹</li>
                    <li><b>РџР°РЅРµР»СЊ РёРЅСЃС‚СЂСѓРјРµРЅС‚РѕРІ</b> вЂ” РєРЅРѕРїРєРё Р±С‹СЃС‚СЂРѕРіРѕ РґРѕСЃС‚СѓРїР°</li>
                    <li><b>РћР±Р»Р°СЃС‚СЊ СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ</b> вЂ” С‚РµРєСЃС‚РѕРІРѕРµ РїРѕР»Рµ РґР»СЏ РІРІРѕРґР° Рё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ С‚РµРєСЃС‚Р°</li>
                    <li><b>РћР±Р»Р°СЃС‚СЊ РІС‹РІРѕРґР° СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ</b> вЂ” РѕР±Р»Р°СЃС‚СЊ РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ СЂР°Р±РѕС‚С‹ Р°РЅР°Р»РёР·Р°С‚РѕСЂР°</li>
                    <li><b>РЎС‚СЂРѕРєР° СЃРѕСЃС‚РѕСЏРЅРёСЏ</b> вЂ” РѕС‚РѕР±СЂР°Р¶Р°РµС‚ РёРЅС„РѕСЂРјР°С†РёСЋ Рѕ СЃРѕСЃС‚РѕСЏРЅРёРё СЂР°Р±РѕС‚С‹ РїСЂРёР»РѕР¶РµРЅРёСЏ</li>
                </ul>

                <h2 id='file-menu'>РњРµРЅСЋ В«Р¤Р°Р№Р»В»</h2>
                <table>
                    <tr>
                        <th>РљРѕРјР°РЅРґР°</th>
                        <th>Р“РѕСЂСЏС‡Р°СЏ РєР»Р°РІРёС€Р°</th>
                        <th>РћРїРёСЃР°РЅРёРµ</th>
                    </tr>
                    <tr>
                        <td><b>РЎРѕР·РґР°С‚СЊ</b></td>
                        <td><span>Ctrl+N</span=></td>
                        <td>РЎРѕР·РґР°РµС‚ РЅРѕРІС‹Р№ РґРѕРєСѓРјРµРЅС‚ РІ РЅРѕРІРѕР№ РІРєР»Р°РґРєРµ</td>
                    </tr>
                    <tr>
                        <td><b>РћС‚РєСЂС‹С‚СЊ</b></td>
                        <td><span>Ctrl+O</span></td>
                        <td>РћС‚РєСЂС‹РІР°РµС‚ СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№ С‚РµРєСЃС‚РѕРІС‹Р№ С„Р°Р№Р»</td>
                    </tr>
                    <tr>
                        <td><b>РЎРѕС…СЂР°РЅРёС‚СЊ</b></td>
                        <td><span>Ctrl+S</span></td>
                        <td>РЎРѕС…СЂР°РЅСЏРµС‚ С‚РµРєСѓС‰РёР№ РґРѕРєСѓРјРµРЅС‚</td>
                    </tr>
                    <tr>
                        <td><b>РЎРѕС…СЂР°РЅРёС‚СЊ РєР°Рє</b></td>
                        <td><span>Ctrl+Shift+S</span></td>
                        <td>РЎРѕС…СЂР°РЅСЏРµС‚ РґРѕРєСѓРјРµРЅС‚ РїРѕРґ РЅРѕРІС‹Рј РёРјРµРЅРµРј</td>
                    </tr>
                    <tr>
                        <td><b>Р’С‹С…РѕРґ</b></td>
                        <td><span>Ctrl+Q</span></td>
                        <td>Р—Р°РІРµСЂС€Р°РµС‚ СЂР°Р±РѕС‚Сѓ РїСЂРѕРіСЂР°РјРјС‹</td>
                    </tr>
                </table>

                <p>РџСЂРё РїРѕРїС‹С‚РєРµ Р·Р°РєСЂС‹С‚СЊ РЅРµСЃРѕС…СЂР°РЅРµРЅРЅС‹Р№ РґРѕРєСѓРјРµРЅС‚ РїСЂРѕРіСЂР°РјРјР° РїСЂРµРґР»РѕР¶РёС‚ СЃРѕС…СЂР°РЅРёС‚СЊ РёР·РјРµРЅРµРЅРёСЏ.</p>

                <h2 id='edit-menu'>РњРµРЅСЋ В«РџСЂР°РІРєР°В»</h2>
                <table>
                    <tr>
                        <th>РљРѕРјР°РЅРґР°</th>
                        <th>Р“РѕСЂСЏС‡Р°СЏ РєР»Р°РІРёС€Р°</th>
                        <th>РћРїРёСЃР°РЅРёРµ</th>
                    </tr>
                    <tr>
                        <td><b>РћС‚РјРµРЅРёС‚СЊ</b></td>
                        <td><span>Ctrl+Z</span></td>
                        <td>РћС‚РјРµРЅСЏРµС‚ РїРѕСЃР»РµРґРЅРµРµ РґРµР№СЃС‚РІРёРµ</td>
                    </tr>
                    <tr>
                        <td><b>РџРѕРІС‚РѕСЂРёС‚СЊ</b></td>
                        <td><span>Ctrl+Y</span></td>
                        <td>РџРѕРІС‚РѕСЂСЏРµС‚ РѕС‚РјРµРЅРµРЅРЅРѕРµ РґРµР№СЃС‚РІРёРµ</td>
                    </tr>
                    <tr>
                        <td><b>Р’С‹СЂРµР·Р°С‚СЊ</b></td>
                        <td><span>Ctrl+X</span></td>
                        <td>РљРѕРїРёСЂСѓРµС‚ РІС‹РґРµР»РµРЅРЅС‹Р№ С‚РµРєСЃС‚ РІ Р±СѓС„РµСЂ Рё СѓРґР°Р»СЏРµС‚ РµРіРѕ</td>
                    </tr>
                    <tr>
                        <td><b>РљРѕРїРёСЂРѕРІР°С‚СЊ</b></td>
                        <td><span>Ctrl+C</span></td>
                        <td>РљРѕРїРёСЂСѓРµС‚ РІС‹РґРµР»РµРЅРЅС‹Р№ С‚РµРєСЃС‚ РІ Р±СѓС„РµСЂ РѕР±РјРµРЅР°</td>
                    </tr>
                    <tr>
                        <td><b>Р’СЃС‚Р°РІРёС‚СЊ</b></td>
                        <td><span>Ctrl+V</span></td>
                        <td>Р’СЃС‚Р°РІР»СЏРµС‚ С‚РµРєСЃС‚ РёР· Р±СѓС„РµСЂР° РѕР±РјРµРЅР°</td>
                    </tr>
                    <tr>
                        <td><b>РЈРґР°Р»РёС‚СЊ</b></td>
                        <td><span>Del</span></td>
                        <td>РЈРґР°Р»СЏРµС‚ РІС‹РґРµР»РµРЅРЅС‹Р№ С‚РµРєСЃС‚</td>
                    </tr>
                    <tr>
                        <td><b>Р’С‹РґРµР»РёС‚СЊ РІСЃС‘</b></td>
                        <td><span>Ctrl+A</span></td>
                        <td>Р’С‹РґРµР»СЏРµС‚ РІРµСЃСЊ С‚РµРєСЃС‚ РІ РґРѕРєСѓРјРµРЅС‚Рµ</td>
                    </tr>
                </table>

                <h2 id='text-menu'>РњРµРЅСЋ В«РўРµРєСЃС‚В»</h2>
                <p>РњРµРЅСЋ В«РўРµРєСЃС‚В» СЃРѕРґРµСЂР¶РёС‚ РёРЅС„РѕСЂРјР°С†РёРѕРЅРЅС‹Рµ СЂР°Р·РґРµР»С‹ Рѕ СЏР·С‹РєРµ Рё РіСЂР°РјРјР°С‚РёРєРµ:</p>
                <ul>
                    <li><b>РџРѕСЃС‚Р°РЅРѕРІРєР° Р·Р°РґР°С‡Рё</b> вЂ” РѕРїРёСЃР°РЅРёРµ С†РµР»Рё Рё Р·Р°РґР°С‡ СЂР°Р±РѕС‚С‹</li>
                    <li><b>Р“СЂР°РјРјР°С‚РёРєР°</b> вЂ” С„РѕСЂРјР°Р»СЊРЅРѕРµ РѕРїРёСЃР°РЅРёРµ РіСЂР°РјРјР°С‚РёРєРё СЏР·С‹РєР°</li>
                    <li><b>РљР»Р°СЃСЃРёС„РёРєР°С†РёСЏ РіСЂР°РјРјР°С‚РёРєРё</b> вЂ” С‚РёРї РіСЂР°РјРјР°С‚РёРєРё РїРѕ РҐРѕРјСЃРєРѕРјСѓ</li>
                    <li><b>РњРµС‚РѕРґ Р°РЅР°Р»РёР·Р°</b> вЂ” РѕРїРёСЃР°РЅРёРµ РјРµС‚РѕРґР° СЃРёРЅС‚Р°РєСЃРёС‡РµСЃРєРѕРіРѕ Р°РЅР°Р»РёР·Р°</li>
                    <li><b>РўРµСЃС‚РѕРІС‹Р№ РїСЂРёРјРµСЂ</b> вЂ” РїСЂРёРјРµСЂ СЂР°Р·Р±РѕСЂР° РІС…РѕРґРЅРѕР№ СЃС‚СЂРѕРєРё</li>
                    <li><b>РЎРїРёСЃРѕРє Р»РёС‚РµСЂР°С‚СѓСЂС‹</b> вЂ” РёСЃРїРѕР»СЊР·РѕРІР°РЅРЅС‹Рµ РёСЃС‚РѕС‡РЅРёРєРё</li>
                    <li><b>РСЃС…РѕРґРЅС‹Р№ РєРѕРґ РїСЂРѕРіСЂР°РјРјС‹</b> вЂ” РєРѕРґ РїСЂРёР»РѕР¶РµРЅРёСЏ</li>
                </ul>
                <p>РџСЂРё РІС‹Р±РѕСЂРµ Р»СЋР±РѕРіРѕ РїСѓРЅРєС‚Р° РѕС‚РєСЂС‹РІР°РµС‚СЃСЏ РѕРєРЅРѕ СЃ СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‰РµР№ РёРЅС„РѕСЂРјР°С†РёРµР№.</p>

                <h2 id='run-menu'>РњРµРЅСЋ В«РџСѓСЃРєВ»</h2>
                <p><b>Р—Р°РїСѓСЃРє Р°РЅР°Р»РёР·Р°С‚РѕСЂР°</b> (<span>F5</span>) вЂ” Р·Р°РїСѓСЃРєР°РµС‚ СЃРёРЅС‚Р°РєСЃРёС‡РµСЃРєРёР№ Р°РЅР°Р»РёР· С‚РµРєСЃС‚Р° РёР· РѕР±Р»Р°СЃС‚Рё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ.</p>

                <p><b>Р РµР·СѓР»СЊС‚Р°С‚С‹ Р°РЅР°Р»РёР·Р°:</b></p>
                <ul>
                    <li>РћС€РёР±РѕС‡РЅС‹Рµ СЃС‚СЂРѕРєРё РѕС‚РјРµС‡Р°СЋС‚СЃСЏ РєСЂР°СЃРЅС‹Рј С†РІРµС‚РѕРј СЃ СѓРєР°Р·Р°РЅРёРµРј РїРѕР·РёС†РёРё РѕС€РёР±РєРё</li>
                    <li>РџСЂРё С‰РµР»С‡РєРµ РЅР° СЃРѕРѕР±С‰РµРЅРёРё РѕР± РѕС€РёР±РєРµ РєСѓСЂСЃРѕСЂ РїРµСЂРµС…РѕРґРёС‚ Рє РѕС€РёР±РѕС‡РЅРѕРјСѓ С„СЂР°РіРјРµРЅС‚Сѓ</li>
                </ul>

                <h2 id='help-menu'>РњРµРЅСЋ В«РЎРїСЂР°РІРєР°В»</h2>
                <table>
                    <tr>
                        <th>РљРѕРјР°РЅРґР°</th>
                        <th>Р“РѕСЂСЏС‡Р°СЏ РєР»Р°РІРёС€Р°</th>
                        <th>РћРїРёСЃР°РЅРёРµ</th>
                    </tr>
                    <tr>
                        <td><b>Р’С‹Р·РѕРІ СЃРїСЂР°РІРєРё</b></td>
                        <td><span>F1</span></td>
                        <td>РћС‚РєСЂС‹РІР°РµС‚ РґР°РЅРЅРѕРµ СЂСѓРєРѕРІРѕРґСЃС‚РІРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ</td>
                    </tr>
                    <tr>
                        <td><b>Рћ РїСЂРѕРіСЂР°РјРјРµ</b></td>
                        <td>F2</td>
                        <td>РРЅС„РѕСЂРјР°С†РёСЏ Рѕ РїСЂРѕРіСЂР°РјРјРµ Рё СЂР°Р·СЂР°Р±РѕС‚С‡РёРєРµ</td>
                    </tr>
                </table>

                <h2>Р Р°Р±РѕС‚Р° СЃ РѕР±Р»Р°СЃС‚СЏРјРё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ Рё РІС‹РІРѕРґР°</h2>
                <p><b>РћР±Р»Р°СЃС‚СЊ СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ:</b> РїСЂРµРґРЅР°Р·РЅР°С‡РµРЅР° РґР»СЏ РІРІРѕРґР° Рё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ С‚РµРєСЃС‚Р°. РџРѕРґРґРµСЂР¶РёРІР°СЋС‚СЃСЏ РІСЃРµ СЃС‚Р°РЅРґР°СЂС‚РЅС‹Рµ РѕРїРµСЂР°С†РёРё СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ.</p>
                <p><b>РћР±Р»Р°СЃС‚СЊ РІС‹РІРѕРґР° СЂРµР·СѓР»СЊС‚Р°С‚РѕРІ:</b> РѕС‚РѕР±СЂР°Р¶Р°РµС‚ СЂРµР·СѓР»СЊС‚Р°С‚С‹ СЂР°Р±РѕС‚С‹ СЃРёРЅС‚Р°РєСЃРёС‡РµСЃРєРѕРіРѕ Р°РЅР°Р»РёР·Р°С‚РѕСЂР°. РћР±Р»Р°СЃС‚СЊ РґРѕСЃС‚СѓРїРЅР° С‚РѕР»СЊРєРѕ РґР»СЏ С‡С‚РµРЅРёСЏ.</p>
                <p><b>РР·РјРµРЅРµРЅРёРµ СЂР°Р·РјРµСЂРѕРІ РѕР±Р»Р°СЃС‚РµР№:</b> РїРµСЂРµС‚Р°СЃРєРёРІР°Р№С‚Рµ СЂР°Р·РґРµР»РёС‚РµР»СЊ РјРµР¶РґСѓ РѕР±Р»Р°СЃС‚СЏРјРё РјС‹С€СЊСЋ.</p>

                <div style="text-align: center; font-size: 16px; font-weight: bold;">
                    <a href="https://github.com/MaKiToShI21/Text-Editor/blob/main/docs/ru/user_manual.md">РџРѕРґСЂРѕР±РЅРѕРµ СЂСѓРєРѕРІРѕРґСЃС‚РІРѕ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ</a>
                </div>

                <div class='footer'>
                    <p>Р Р°Р·СЂР°Р±РѕС‚Р°РЅРѕ СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј PyQt6</p>
                    <p>В© 2026 MaKiToShI</p>
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
                    <p><b>Text editor</b> вЂ” This application is for creating and editing text documents with parsing capabilities. The program provides a user-friendly interface for working with text and supports all basic editing operations.</p>

                    <h2 id='interface'>Program interface</h2>
                    <p>The main window of the text editor consists of the following elements:</p>
                    <ul>
                        <li><b>Window title</b> вЂ” displays the program name and the name of the current file</li>
                        <li><b>Main menu</b> вЂ” contains all available commands</li>
                        <li><b>Toolbar</b> вЂ” quick access buttons</li>
                        <li><b>Editing area</b> вЂ” a text field for entering and editing text</li>
                        <li><b>Results output area</b> вЂ” area for displaying the analyzer's results</li>
                        <li><b>Status bar</b> вЂ” displays information about the application's running status</li>
                    </ul>

                    <h2 id='file-menu'>Menu В«FileВ»</h2>
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

                    <h2 id='edit-menu'>Menu В«EditВ»</h2>
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

                    <h2 id='text-menu'>Menu В«TextВ»</h2>
                    <p>Menu В«TextВ» contains information sections on language and grammar:</p>
                    <ul>
                        <li><b>Statement of the problem</b> вЂ” description of the purpose and objectives of the work</li>
                        <li><b>Grammar</b> вЂ” formal description of the grammar of a language</li>
                        <li><b>Classification of grammar</b> вЂ” Chomsky's type of grammar</li>
                        <li><b>Method of analysis</b> вЂ” description of the syntactic analysis method</li>
                        <li><b>Test example</b> вЂ” example of parsing an input string</li>
                        <li><b>Bibliography</b> вЂ” sources used</li>
                        <li><b>Source code of the program</b> вЂ” program code</li>
                    </ul>
                    <p>When you select any item, a window with the corresponding information opens.</p>

                    <h2 id='run-menu'>Menu В«RunВ»</h2>
                    <p><b>Launching the analyzer</b> (<span>F5</span>) вЂ” starts parsing the text from the editing area.</p>

                    <p><b>Results of the analysis:</b></p>
                    <ul>
                        <li>Erroneous lines are marked in red with the position of the error indicated.</li>
                        <li>Clicking on an error message moves the cursor to the erroneous section</li>
                    </ul>

                    <h2 id='help-menu'>Menu В«HelpВ»</h2>
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
                        <p>В© 2026 MaKiToShI</p>
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
            dialog.setWindowTitle("Рћ РїСЂРѕРіСЂР°РјРјРµ")
            text_browser.setHtml("""
                <div style='text-align: center;'>
                    <h1>РўРµРєСЃС‚РѕРІС‹Р№ СЂРµРґР°РєС‚РѕСЂ</h1>
                    <p style='color: #868e94; font-size: 14px;'>Р’РµСЂСЃРёСЏ 1.0.0</p>

                    <div style='padding: 5px;'>
                        <p style='font-size: 16px; line-height: 1;'>
                            РџСЂРѕРіСЂР°РјРјР° РґР»СЏ СЂРµРґР°РєС‚РёСЂРѕРІР°РЅРёСЏ С‚РµРєСЃС‚РѕРІС‹С… С„Р°Р№Р»РѕРІ<br>
                            СЃ РІРѕР·РјРѕР¶РЅРѕСЃС‚СЊСЋ СЃРёРЅС‚Р°РєСЃРёС‡РµСЃРєРѕРіРѕ Р°РЅР°Р»РёР·Р°
                        </p>
                    </div>

                    <div>
                        <p><b>Р Р°Р·СЂР°Р±РѕС‚С‡РёРє:</b> MaKiToShI</p>
                        <p><b>Р“РѕРґ:</b> 2026</p>
                    </div>

                    <div style='border-top: 1px solid #dee2e6; padding-top: 15px;'>
                        <p style='color: #868e94; font-size: 12px;'>
                            Р Р°Р·СЂР°Р±РѕС‚Р°РЅРѕ СЃ РёСЃРїРѕР»СЊР·РѕРІР°РЅРёРµРј PyQt6<br>
                            В© 2026 MaKiToShI
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
                        <p><b>Р“РѕРґ:</b> 2026</p>
                    </div>

                    <div style='border-top: 1px solid #dee2e6; padding-top: 15px;'>
                        <p style='color: #868e94; font-size: 12px;'>
                            Developed using PyQt6<br>
                            В© 2026 MaKiToShI
                        </p>
                    </div>
                </div>
                """)

        text_browser.setOpenExternalLinks(True)
        text_browser.setReadOnly(True)
        layout.addWidget(text_browser)
        dialog.exec()
