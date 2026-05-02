from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QFileDialog,
                             QMessageBox, QDialog, QTextBrowser,
                             QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QWidget)
from PyQt6.QtGui import QAction, QDesktopServices
from semantic_analyzer import SemanticAnalyzer
from language import Language, LanguageDialog
from code_editor import CodeEditor
from lexer import LexicalAnalyzer
from PyQt6.QtCore import Qt, QUrl
from ui import Ui_MainWindow
from parser import Parser
from PyQt6 import QtGui
import sys
import re
import os


class TextEditor(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # loadUi('text_editor.ui', self)
        self.setupUi(self)
        self.addIcons()

        self.setMinimumSize(500, 400)

        self.lang = Language()
        self.apply_language()

        self.status_bar = self.statusBar
        self.lexer_process = None
        self.current_input_widget = None
        self.current_tab_name = None
        self.current_file_path = None
        self.result_table = None
        self.errors_table = None
        self.ast_browser = None
        self.astTab = None
        self.resultTab = None
        self.ErrorTab = None

        self.setAcceptDrops(True)
        self.setup_actions()

    @staticmethod
    def resource_path(relative_path):
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, relative_path)

    def addIcons(self):
        self.actionNew.setIcon(QtGui.QIcon(self.resource_path("icons/new_file.png")))
        self.actionOpen.setIcon(QtGui.QIcon(self.resource_path("icons/open_folder.png")))
        self.actionSave.setIcon(QtGui.QIcon(self.resource_path("icons/save_file.png")))
        self.actionSaveAs.setIcon(QtGui.QIcon(self.resource_path("icons/save_file_as.png")))
        self.actionExit.setIcon(QtGui.QIcon(self.resource_path("icons/exit.png")))

        self.actionUndo.setIcon(QtGui.QIcon(self.resource_path("icons/undo.png")))
        self.actionRedo.setIcon(QtGui.QIcon(self.resource_path("icons/redo.png")))
        self.actionCopy.setIcon(QtGui.QIcon(self.resource_path("icons/copy.png")))
        self.actionPaste.setIcon(QtGui.QIcon(self.resource_path("icons/paste.png")))
        self.actionCut.setIcon(QtGui.QIcon(self.resource_path("icons/cut.png")))
        self.actionDelete.setIcon(QtGui.QIcon(self.resource_path("icons/delete.png")))
        self.actionSelectAll.setIcon(QtGui.QIcon(self.resource_path("icons/select_all.png")))

        self.actionHelp.setIcon(QtGui.QIcon(self.resource_path("icons/help.png")))
        self.actionAbout.setIcon(QtGui.QIcon(self.resource_path("icons/about.png")))
        self.actionLanguage.setIcon(QtGui.QIcon(self.resource_path("icons/language.png")))

        self.actionRunLexer.setIcon(QtGui.QIcon(self.resource_path("icons/run.png")))
        self.actionRunParser.setIcon(QtGui.QIcon(self.resource_path("icons/run.png")))

    def setup_actions(self):
        action_map = {
            'actionOpen': self.open_file,
            'actionNew': self.new_file,
            'actionSave': self.save_file,
            'actionSaveAs': self.save_file_as,
            'actionExit': self.exit_app,
            'actionOpenProblemStatement': self.open_problem_statement,
            'actionOpenStateDiagram': self.open_state_diagram,
            'actionOpenGrammar': self.open_grammar,
            'actionOpenGrammarClass': self.open_grammar_class,
            'actionOpenAnalysisMethod': self.open_analysis_method,
            'actionDiagnosticsTroubleshooting': self.open_diagnostics_troubleshooting,
            'actionOpenExample': self.open_example,
            'actionOpenReferences': self.open_references,
            'actionOpenSourceCode': self.open_source_code,
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
        self.output_tab_widget.setTabsClosable(False)

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
            'actionOpenProblemStatement', 'actionOpenStateDiagram',
            'actionOpenGrammar', 'actionOpenGrammarClass',
            'actionOpenAnalysisMethod', 'actionDiagnosticsTroubleshooting',
            'actionOpenExample', 'actionOpenReferences',
            'actionOpenSourceCode', 'actionRunLexer', 'actionRunParser',
            'actionHelp', 'actionAbout',
            'actionLanguage',
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
        self._update_output_tab_titles()

    def setup_output_panels(self):
        self._ensure_output_tabs()

        if self.result_table is None:
            self.result_table = QTableWidget(self.resultTab)
            result_layout = QVBoxLayout(self.resultTab)
            result_layout.setContentsMargins(0, 0, 0, 0)
            result_layout.addWidget(self.result_table)

        if self.errors_table is None:
            self.errors_table = QTableWidget(self.ErrorTab)
            errors_layout = QVBoxLayout(self.ErrorTab)
            errors_layout.setContentsMargins(0, 0, 0, 0)
            errors_layout.addWidget(self.errors_table)

        if self.ast_browser is None:
            self.ast_browser = QTextBrowser(self.astTab)
            self.ast_browser.setReadOnly(True)
            ast_layout = QVBoxLayout(self.astTab)
            ast_layout.setContentsMargins(0, 0, 0, 0)
            ast_layout.addWidget(self.ast_browser)

        self._update_output_tab_titles()

    def _ensure_output_tabs(self):
        if not hasattr(self, 'output_tab_widget') or self.output_tab_widget is None:
            return

        if not hasattr(self, 'resultTab') or self.resultTab is None:
            self.resultTab = QWidget()
            self.resultTab.setObjectName("resultTab")
            self.output_tab_widget.addTab(self.resultTab, "")

        if not hasattr(self, 'ErrorTab') or self.ErrorTab is None:
            self.ErrorTab = QWidget()
            self.ErrorTab.setObjectName("ErrorTab")
            self.output_tab_widget.addTab(self.ErrorTab, "")

        if not hasattr(self, 'astTab') or self.astTab is None:
            self.astTab = QWidget()
            self.astTab.setObjectName("astTab")
            self.output_tab_widget.addTab(self.astTab, "")

    def _update_output_tab_titles(self):
        if not hasattr(self, 'output_tab_widget') or self.output_tab_widget is None:
            return
        if self.resultTab is None or self.ErrorTab is None or self.astTab is None:
            return

        result_index = self.output_tab_widget.indexOf(self.resultTab)
        if result_index >= 0:
            self.output_tab_widget.setTabText(
                result_index,
                self.lang.translate('output_tab_result')
            )

        errors_index = self.output_tab_widget.indexOf(self.ErrorTab)
        if errors_index >= 0:
            self.output_tab_widget.setTabText(
                errors_index,
                self.lang.translate('output_tab_errors')
            )

        ast_index = self.output_tab_widget.indexOf(self.astTab)
        if ast_index >= 0:
            self.output_tab_widget.setTabText(
                ast_index,
                self.lang.translate('output_tab_ir')
            )

    def clear_output_views(self):
        self._clear_table_widget(self.result_table)
        self._clear_table_widget(self.errors_table)
        if self.ast_browser is not None:
            self.ast_browser.setPlainText(self.lang.translate('ast_not_available'))

    @staticmethod
    def _clear_table_widget(table):
        if table is None:
            return
        table.clear()
        table.clearContents()
        table.setRowCount(0)
        table.setColumnCount(0)

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
            QMessageBox.critical(
                self,
                self.lang.translate('error'),
                self.lang.translate('opening_error').format(str(e), 0)
            )
            return False

    def close_input_tab(self, index):
        widget = self.input_tab_widget.widget(index)
        tab_name = self.input_tab_widget.tabText(index)

        def closing():
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
        _ = index
        return

    def can_close(self):
        for i in range(self.input_tab_widget.count()):
            widget = self.input_tab_widget.widget(i)
            if not widget.isModified():
                continue
            tab_name = self.input_tab_widget.tabText(i)

            reply = QMessageBox.question(
                self,
                self.lang.translate('unsaved_changes'),
                self.lang.translate('save_changes').format(tab_name, 0),
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

    def _open_info_html(self, filename):
        info_dir = self.resource_path('information')

        file_path = os.path.join(info_dir, filename)

        if not os.path.isfile(file_path):
            QMessageBox.critical(
                self,
                self.lang.translate('error'),
                self.lang.translate('opening_error').format(file_path)
            )
            return

        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def open_problem_statement(self):
        self._open_info_html('problem_statement.html')

    def open_state_diagram(self):
        self._open_info_html('state_diagram.html')

    def open_grammar(self):
        self._open_info_html('grammar.html')

    def open_grammar_class(self):
        self._open_info_html('grammar_classification.html')

    def open_analysis_method(self):
        self._open_info_html('analysis_method.html')

    def open_diagnostics_troubleshooting(self):
        self._open_info_html('diagnostics_troubleshooting.html')

    def open_example(self):
        example_path = self.resource_path("example.txt")
        example_text = (
            "(17 + 3 * 5) % 7 - 2"
        )
        normalized_example_path = os.path.normcase(os.path.normpath(example_path))

        for i in range(self.input_tab_widget.count()):
            editor = self.input_tab_widget.widget(i)
            tab_file_path = getattr(editor, 'file_path', None)
            if not tab_file_path:
                continue

            normalized_tab_path = os.path.normcase(os.path.normpath(tab_file_path))
            if normalized_tab_path == normalized_example_path:
                editor.setText(example_text)
                editor.setModified(False)
                self.input_tab_widget.setCurrentIndex(i)
                return

        self.create_new_tab("example.txt", example_text, example_path)

    def open_references(self):
        self._open_info_html('references.html')

    def open_source_code(self):
        QDesktopServices.openUrl(QUrl("https://github.com/MaKiToShI21/Text-Editor"))

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
            QMessageBox.critical(
                self,
                self.lang.translate('error'),
                self.lang.translate('file_saving_error').format(str(e))
            )
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
                self,
                self.lang.translate('error'),
                self.lang.translate('file_saving_error').format(str(e), 0)
            )
            return False

    def _get_active_editor_for_analysis(self):
        if not self.input_tab_widget:
            return None

        index = self.input_tab_widget.currentIndex()
        if index < 0:
            return None

        widget = self.input_tab_widget.widget(index)
        if not isinstance(widget, CodeEditor):
            return None
        return widget

    def runLexer(self):
        if not self.input_tab_widget:
            return
        self.setup_output_panels()
        index = self.input_tab_widget.currentIndex()
        self.current_input_widget = self._get_active_editor_for_analysis()
        if self.current_input_widget is None:
            self.status_bar.showMessage(self.lang.translate('text_edit_inactive'), 3000)
            return
        text = self.current_input_widget.text()
        if not text or not text.strip():
            self.status_bar.showMessage(self.lang.translate('lexer_input_empty'), 5000)
            return

        self.current_file_path = self.current_input_widget.file_path

        if not self.current_file_path or self.current_input_widget.isModified():
            if not self.save_file():
                return
            if self.current_input_widget.file_path:
                self.current_file_path = self.current_input_widget.file_path

        self.current_tab_name = self.input_tab_widget.tabText(index)
        self.clear_output_views()

        lexer = LexicalAnalyzer(self.lang)
        tokens, errors = lexer.analyze(text)
        self.fill_table(tokens, [], self.result_table)
        if errors:
            self.fill_table([], errors, self.errors_table)
        else:
            self._clear_table_widget(self.errors_table)
        if len(errors) == 0:
            self.status_bar.showMessage(self.lang.translate('no_errors'), 10000)
        else:
            self.status_bar.showMessage(self.lang.translate('total_errors').format(len(errors), 0), 10000)

    def runParser(self):
        if not self.input_tab_widget:
            return
        self.setup_output_panels()
        index = self.input_tab_widget.currentIndex()
        self.current_input_widget = self._get_active_editor_for_analysis()
        if self.current_input_widget is None:
            self.status_bar.showMessage(self.lang.translate('text_edit_inactive'), 3000)
            return
        text = self.current_input_widget.text()
        if not text or not text.strip():
            self.status_bar.showMessage(self.lang.translate('parser_input_empty'), 5000)
            return

        self.current_file_path = self.current_input_widget.file_path

        if not self.current_file_path or self.current_input_widget.isModified():
            if not self.save_file():
                return
            if self.current_input_widget.file_path:
                self.current_file_path = self.current_input_widget.file_path

        self.current_tab_name = self.input_tab_widget.tabText(index)
        self.clear_output_views()

        parser = Parser(self.lang)
        session = parser.analyze(text, collect_ir=True)
        self.fill_table(session.tokens, [], self.result_table)

        ir_report = SemanticAnalyzer(self.lang).format_ir_report(session)
        errors = session.errors

        if errors:
            self.fill_parser_table(errors, self.errors_table)
        else:
            self._clear_table_widget(self.errors_table)
        if self.ast_browser is not None:
            self.ast_browser.setPlainText(ir_report)
        if len(errors) == 0:
            self.status_bar.showMessage(self.lang.translate('no_errors'), 10000)
        else:
            self.status_bar.showMessage(self.lang.translate('total_errors').format(len(errors), 0), 10000)

    @staticmethod
    def _extract_location(location):
        numbers = re.findall(r"\d+", location or "")
        if len(numbers) < 3:
            return None, None, None
        return int(numbers[0]), int(numbers[1]), int(numbers[2])

    def get_token_type(self, code):
        lexer = LexicalAnalyzer(self.lang)
        return lexer.TOKEN_TYPES.get(code, self.lang.translate('unknown_code').format(code, 0))

    def create_or_update_table(self, tokens, errors):
        self.fill_table(tokens, errors, self.result_table)

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

        total_rows = len(errors) + len(tokens)
        rowLables = []

        if total_rows > 0:
            table.setRowCount(total_rows)

            for row, error in enumerate(errors):
                item_code = QTableWidgetItem(str(error['code']))
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

            token_start_row = len(errors)
            for i, token in enumerate(tokens):
                row = token_start_row + i
                item_code = QTableWidgetItem(str(token['code']))
                item_code.setForeground(Qt.GlobalColor.white)
                table.setItem(row, 0, item_code)

                item_type = QTableWidgetItem(token['type'])
                item_type.setForeground(Qt.GlobalColor.white)
                table.setItem(row, 1, item_type)

                item_lexeme = QTableWidgetItem(token['lexeme'])
                item_lexeme.setForeground(Qt.GlobalColor.white)
                table.setItem(row, 2, item_lexeme)

                item_loc = QTableWidgetItem(token['location'])
                item_loc.setForeground(Qt.GlobalColor.white)
                table.setItem(row, 3, item_loc)

                rowLables.append(str(row + 1))
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
        self.fill_parser_table(errors, self.errors_table)

    def fill_parser_table(self, errors, table=None):
        if table:
            table.clearContents()
            table.setRowCount(0)
        else:
            table = QTableWidget(self)

        table.setColumnCount(4)
        table.setHorizontalHeaderLabels([
            self.lang.translate('parser_wrong_fragment'),
            self.lang.translate('analysis_type'),
            self.lang.translate('parser_error_description'),
            self.lang.translate('location'),
        ])

        row_labels = []
        if errors:
            table.setRowCount(len(errors))
            for row, error in enumerate(errors):
                fragment = QTableWidgetItem(error.get('lexeme', ''))
                fragment.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 0, fragment)

                error_kind = error.get("analysis_type", "syntax")
                if error_kind == "semantic":
                    type_text = self.lang.translate("semantic_kind")
                elif error_kind == "lexical":
                    type_text = self.lang.translate("lexical_kind")
                else:
                    type_text = self.lang.translate("syntax_kind")
                kind_item = QTableWidgetItem(type_text)
                kind_item.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 1, kind_item)

                description_text = error.get('description', error.get('type', ''))
                description = QTableWidgetItem(description_text)
                description.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 2, description)

                location = QTableWidgetItem(error.get('location', ''))
                location.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 3, location)

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

        location_item = self._get_location_item(table, row, fallback_col=3)
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

    def on_semantic_table_item_clicked(self, item):
        row = item.row()
        table = item.tableWidget()

        location_item = self._get_location_item(table, row, fallback_col=1)
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
                line_index = line_num - 1
                line_start_pos = editor.SendScintilla(editor.SCI_POSITIONFROMLINE, line_index)
                line_text = editor.text(line_index)

                start_bytes = len(line_text[:max(start_col - 1, 0)].encode('utf-8'))
                end_bytes = len(line_text[:max(end_col, 0)].encode('utf-8'))

                start_pos = line_start_pos + start_bytes
                end_pos = line_start_pos + end_bytes

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
        _ = table
        return

    def create_or_update_semantic_table(self, errors):
        self.fill_parser_table(errors, self.errors_table)

    def fill_semantic_table(self, errors, table=None):
        if table:
            table.clearContents()
            table.setRowCount(0)
        else:
            table = QTableWidget(self)

        table.setColumnCount(2)
        table.setHorizontalHeaderLabels([
            self.lang.translate('semantic_message'),
            self.lang.translate('semantic_position'),
        ])

        row_labels = []
        if errors:
            table.setRowCount(len(errors))
            for row, error in enumerate(errors):
                message = QTableWidgetItem(error.get('message', ''))
                message.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 0, message)

                location = QTableWidgetItem(error.get('location', ''))
                location.setForeground(Qt.GlobalColor.red)
                table.setItem(row, 1, location)

                row_labels.append(str(row + 1))
            self._rebind_table_click_handler(table, self.on_semantic_table_item_clicked)
        else:
            table.setRowCount(0)

        table.setVerticalHeaderLabels(row_labels)
        table.resizeColumnsToContents()
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        return table

    def edit_action(self, action_name, method_name):
        widget = self.get_current_input_tab_widget()
        action = f"{action_name}_status_bar"
        if widget:
            getattr(widget, method_name)()
            self.status_bar.showMessage(self.lang.translate(action), 3000)

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
                <div class='version'>Руководство пользователя | Версия 2.0.0</div>

                <p><b>Текстовый редактор</b> — это приложение для создания и редактирования текстовых документов с возможностью синтаксического анализа. Программа предоставляет удобный интерфейс для работы с текстом и поддерживает все основные операции редактирования.</p>

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
                <p>Меню «Текст» содержит информационные разделы:</p>
                <ul>
                    <li><b>Постановка задачи</b> — описание цели и задач работы</li>
                    <li><b>Тестовый пример</b> — пример разбора входной строки</li>
                    <li><b>Список литературы</b> — использованные источники</li>
                    <li><b>Исходный код программы</b> — код приложения</li>
                </ul>

                <h2 id='run-menu'>Меню «Пуск»</h2>
                <p><b>Запуск лексического анализатора</b> (<span>F5</span>) — запускает лексический анализ текста из области редактирования.</p>
                <p><b>Запуск парсера анализатора</b> (<span>F6</span>) — запускает синтаксический анализ текста из области редактирования.</p>

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
                    <div class='version'>User Manual | Version 2.0.0</div>

                    <p><b>Text editor</b> — is an application is for creating and editing text documents with parsing capabilities. The program provides a user-friendly interface for working with text and supports all basic editing operations.</p>

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
                    <p>Menu «Text» contains information sections:</p>
                    <ul>
                        <li><b>Statement of the problem</b> — description of the purpose and objectives of the work</li>
                        <li><b>Test example</b> — example of parsing an input string</li>
                        <li><b>Bibliography</b> — sources used</li>
                        <li><b>Source code of the program</b> — program code</li>
                    </ul>

                    <h2 id='run-menu'>Menu «Run»</h2>
                    <p><b>Launching the lexical analyzer</b> (<span>F5</span>) — starts lexical analysis of the text in the editing area.</p>
                    <p><b>Launching the syntax analyzer</b> (<span>F6</span>) — starts parsing the text from the editing area.</p>

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
        dialog.setMinimumWidth(525)
        dialog.setMinimumHeight(300)
        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        if self.lang.current_language == 'ru':
            dialog.setWindowTitle("О программе")
            text_browser.setHtml("""
                <div style='text-align: center;'>
                    <h1 style='color: #ffffff;'>Текстовый редактор</h1>
                    <p style='color: #868e94; font-size: 14px;'>Версия 2.0.0</p>

                    <div style='padding: 5px;'>
                        <p style='color: #ffffff; font-size: 16px; line-height: 1;'>
                            Программа для редактирования текстовых файлов<br>
                            с возможностью синтаксического анализа
                        </p>
                    </div>

                    <div style='color: #ffffff;'>
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
                    <h1 style='color: #ffffff;'>Text editor</h1>
                    <p style='color: #868e94; font-size: 14px;'>Version 2.0.0</p>

                    <div style='padding: 5px;'>
                        <p style='color: #ffffff; font-size: 16px; line-height: 1;'>
                            A program for editing text files with syntax analysis capabilities
                        </p>
                    </div>

                    <div style='color: #ffffff;>
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
