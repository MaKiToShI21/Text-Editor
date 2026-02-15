from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QTabWidget, QFileDialog, QMessageBox,
                             QListWidget, QDialog, QTextBrowser,
                             QVBoxLayout)
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QRadioButton,
                             QDialogButtonBox, QButtonGroup)
from PyQt6.QtGui import QAction, QColor, QDragEnterEvent, QDropEvent
from PyQt6.Qsci import QsciScintilla, QsciLexerPython
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt
import sys
import os
# from ui_editor import Ui_MainWindow


class LanguageDialog(QDialog):
    def __init__(self, current_language='ru', parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор языка")
        self.setFixedSize(300, 200)

        self.selected_language = current_language

        layout = QVBoxLayout(self)

        title_label = QLabel("Выберите язык интерфейса:")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title_label)

        self.radio_group = QButtonGroup(self)

        self.rb_russian = QRadioButton("Русский")
        self.rb_russian.setChecked(current_language == 'ru')
        self.rb_russian.toggled.connect(lambda: self.set_language('ru'))
        layout.addWidget(self.rb_russian)
        self.radio_group.addButton(self.rb_russian)

        self.rb_english = QRadioButton("English")
        self.rb_english.setChecked(current_language == 'en')
        self.rb_english.toggled.connect(lambda: self.set_language('en'))
        layout.addWidget(self.rb_english)
        self.radio_group.addButton(self.rb_english)

        layout.addStretch()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def set_language(self, lang):
        self.selected_language = lang

    def get_selected_language(self):
        return self.selected_language


class TextEditor(QMainWindow):  # , Ui_MainWindow
    def __init__(self):
        super().__init__()
        loadUi('text_editor.ui', self)
        # self.setupUi(self)

        # Словарь с переводами для всех элементов
        self.translations = {
            'ru': {
                # Window title
                'window_title': 'Текстовый редактор',

                # Menus
                'menuFile': 'Файл',
                'menuEdit': 'Правка',
                'menuText': 'Текст',
                'menuRun': 'Пуск',
                'menuHelp': 'Справка',
                'menuSettings': 'Настройки',

                # File menu actions
                'actionNew': 'Создать',
                'actionOpen': 'Открыть',
                'actionSave': 'Сохранить',
                'actionSaveAs': 'Сохранить как',
                'actionExit': 'Выход',

                # Edit menu actions
                'actionUndo': 'Отменить',
                'actionRedo': 'Повторить',
                'actionCut': 'Вырезать',
                'actionCopy': 'Копировать',
                'actionPaste': 'Вставить',
                'actionDelete': 'Удалить',
                'actionSelectAll': 'Выделить всё',

                # Tooltip for actions
                'actionNew_toolTip': 'Создать',
                'actionOpen_toolTip': 'Открыть',
                'actionRedo_toolTip': 'Повторить',
                'actionRun_toolTip': 'Пуск',

                # Text menu actions
                'action_15': 'Постановка задачи',
                'action_16': 'Грамматика',
                'action_17': 'Классификация грамматики',
                'action_18': 'Метод анализа',
                'action_19': 'Тестовый пример',
                'action_20': 'Список литературы',
                'action_21': 'Исходный код программы',

                # Run menu actions
                'actionRun': 'Пуск',

                # Help menu actions
                'actionHelp': 'Вызов справки',
                'actionAbout': 'О программе',

                # Settings menu actions
                'actionLanguage': 'Язык',

                # Default tab titles
                'new_document': 'Новый документ',

                # Messages
                'file_saved': 'Файл сохранен',
                'file_opened': 'Файл открыт',
                'unsaved_changes': 'Несохраненные изменения',
                'save_changes': 'Сохранить изменения в',
                'tab_closed': 'Вкладка закрыта',
                'copied': 'Скопировано',
                'pasted': 'Вставлено',
                'cut': 'Вырезано',
                'deleted': 'Удалено',
                'selected_all': 'Выделено всё',
                'undo': 'Отмена',
                'redo': 'Повтор',
                'language_changed': 'Язык изменен на русский',
                'drop_hint': 'Отпустите файл для открытия',
                'opening_files': 'Открываю {} файлов...',
                'opened_files': 'Открыто файлов: {}',
                'tab_close_cancelled': 'Закрытие вкладки отменено',
                'text_edit_inactive': 'Текстовое поле не активно',
                'encoding_error': 'Не удалось открыть файл (ошибка кодировки)',
                'error': 'Ошибка',
                'save_cancelled': 'Сохранение отменено',
            },
            'en': {
                # Window title
                'window_title': 'Text Editor',

                # Menus
                'menuFile': 'File',
                'menuEdit': 'Edit',
                'menuText': 'Text',
                'menuRun': 'Run',
                'menuHelp': 'Help',
                'menuSettings': 'Settings',

                # File menu actions
                'actionNew': 'New',
                'actionOpen': 'Open',
                'actionSave': 'Save',
                'actionSaveAs': 'Save As',
                'actionExit': 'Exit',

                # Edit menu actions
                'actionUndo': 'Undo',
                'actionRedo': 'Redo',
                'actionCut': 'Cut',
                'actionCopy': 'Copy',
                'actionPaste': 'Paste',
                'actionDelete': 'Delete',
                'actionSelectAll': 'Select All',

                # Tooltip for actions
                'actionNew_toolTip': 'Create',
                'actionOpen_toolTip': 'Open',
                'actionRedo_toolTip': 'Redo',
                'actionRun_toolTip': 'Run',

                # Text menu actions
                'action_15': 'Problem Statement',
                'action_16': 'Grammar',
                'action_17': 'Grammar Classification',
                'action_18': 'Analysis Method',
                'action_19': 'Test Example',
                'action_20': 'References',
                'action_21': 'Source Code',

                # Run menu actions
                'actionRun': 'Run',

                # Help menu actions
                'actionHelp': 'Help',
                'actionAbout': 'About',

                # Settings menu actions
                'actionLanguage': 'Language',

                # Default tab titles
                'new_document': 'New Document',

                # Messages
                'file_saved': 'File saved',
                'file_opened': 'File opened',
                'unsaved_changes': 'Unsaved Changes',
                'save_changes': 'Save changes in',
                'tab_closed': 'Tab closed',
                'copied': 'Copied',
                'pasted': 'Pasted',
                'cut': 'Cut',
                'deleted': 'Deleted',
                'selected_all': 'Selected all',
                'undo': 'Undo',
                'redo': 'Redo',
                'language_changed': 'Language changed to English',
                'drop_hint': 'Drop files to open',
                'opening_files': 'Opening {} file(s)...',
                'opened_files': 'Opened files: {}',
                'tab_close_cancelled': 'Tab close cancelled',
                'text_edit_inactive': 'Text edit not active',
                'encoding_error': 'Could not open file (encoding error)',
                'error': 'Error',
                'save_cancelled': 'Save cancelled',
            }
        }

        self.current_language = 'ru'

        self.load_language_setting()
        self.apply_language()

        self.setAcceptDrops(True)
        self.setup_actions()

        self.input_tab_widget = self.findChild(QTabWidget, 'inputTabWidget')
        self.input_tab_widget.tabCloseRequested.connect(self.close_tab)

        self.output_tab_widget = self.findChild(QTabWidget, 'outputTabWidget')
        self.output_tab_widget.tabCloseRequested.connect(self.close_tab)

        self.status_bar = self.statusBar
        self.file_paths = {}

    def tr(self, key):
        return self.translations[self.current_language].get(key, key)

    def show_language_dialog(self):
        dialog = LanguageDialog(self.current_language, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_language = dialog.get_selected_language()

            if new_language != self.current_language:
                self.current_language = new_language
                self.save_language_setting()
                self.apply_language()

                self.status_bar.showMessage(self.tr('language_changed'), 3000)

    def save_language_setting(self):
        try:
            with open('language_config.txt', 'w', encoding='utf-8') as f:
                f.write(self.current_language)
        except:
            pass

    def load_language_setting(self):
        try:
            with open('language_config.txt', 'r', encoding='utf-8') as f:
                self.current_language = f.read().strip()
        except:
            pass

    def apply_language(self):
        t = self.translations[self.current_language]

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
                text_edit = self.input_tab_widget.widget(i)
                if id(text_edit) not in self.file_paths:
                    self.input_tab_widget.setTabText(i, t['new_document'])

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

    def dragEnterEvent(self, event: QDragEnterEvent | None):
        if event is None:
            return

        mime_data = event.mimeData()
        if mime_data is None:
            return

        if mime_data.hasUrls():
            event.acceptProposedAction()
            self.status_bar.showMessage(self.tr('drop_hint'), 0)
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
            self.status_bar.showMessage(
                self.tr('opening_files').format(len(files)), 0)
            QApplication.processEvents()

            opened = 0
            for file_path in files:
                if os.path.isfile(file_path):
                    if self.open_dropped_file(file_path):
                        opened += 1

            self.status_bar.showMessage(
                self.tr('opened_files').format(opened), 3000)

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
                self.tr('unsaved_changes'),
                self.tr('save_changes') + f" '{tab_name}'?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self.input_tab_widget.setCurrentIndex(index)

                saved = self.save_file()

                if not saved:
                    self.status_bar.showMessage(
                        self.tr('tab_close_cancelled'), 3000)
                    return

            elif reply == QMessageBox.StandardButton.Cancel:
                self.status_bar.showMessage(
                    self.tr('tab_close_cancelled'), 3000)
                return

        if id(text_edit) in self.file_paths:
            del self.file_paths[id(text_edit)]

        self.input_tab_widget.removeTab(index)
        text_edit.deleteLater()

        self.status_bar.showMessage(
            f"{self.tr('tab_closed')} '{tab_name}'", 3000)

    def close(self):
        for i in range(self.input_tab_widget.count()):
            text_edit = self.input_tab_widget.widget(i)
            if text_edit.isModified():
                tab_name = self.input_tab_widget.tabText(i)

                reply = QMessageBox.question(
                    self,
                    self.tr('unsaved_changes'),
                    self.tr('save_changes') + f" '{tab_name}'?",
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

    def create_new_tab(self, title=None, content="", file_path=None):
        text_edit = CodeEditor()
        text_edit.setText(content)

        if title is None:
            title = self.tr('new_document')

        index = self.input_tab_widget.addTab(text_edit, title)

        if file_path:
            self.file_paths[id(text_edit)] = file_path
        text_edit.setModified(False)

        self.input_tab_widget.setCurrentIndex(index)

        if file_path:
            self.status_bar.showMessage(f"{self.tr('file_opened')} {title}",
                                        3000)
        else:
            self.status_bar.showMessage(f"{title}", 3000)

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
                    self.tr('file_saved') + f" {os.path.basename(file_path)}",
                    3000)

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
            self.status_bar.showMessage(self.tr('actionUndo'), 3000)

    def redo(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.redo()
            self.status_bar.showMessage(self.tr('actionRedo'), 3000)

    def copy(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.copy()
            self.status_bar.showMessage(self.tr('actionCopy'), 3000)

    def paste(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.paste()
            self.status_bar.showMessage(self.tr('actionPaste'), 3000)

    def cut(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.cut()
            self.status_bar.showMessage(self.tr('actionCut'), 3000)

    def delete(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            if text_edit.hasSelectedText():
                text_edit.removeSelectedText()
                self.status_bar.showMessage(self.tr('actionDelete'), 3000)

    def select_all(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            text_edit.selectAll()
            self.status_bar.showMessage(self.tr('actionSelectAll'), 3000)

    def get_current_text_edit(self):
        if hasattr(self, 'input_tab_widget') and self.input_tab_widget:
            current_widget = self.input_tab_widget.currentWidget()
            if isinstance(current_widget, (QTextEdit, QsciScintilla)):
                return current_widget
            else:
                self.status_bar.showMessage(self.tr('actionRedo'), 3000)
                self.status_bar.showMessage(self.tr('text_edit_inactive'),
                                            3000)
                return None
        return None

    def help(self):
        dialog = QDialog(self)

        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(600)

        dialog.setStyleSheet("background-color: #2b2b2b;")

        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()

        if self.current_language == 'ru':
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
        else:
            if self.current_language == 'en':
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
                    <div class='version'>User Manual | Version 1.0</div>

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
        dialog.setMinimumHeight(350)
        layout = QVBoxLayout(dialog)
        text_browser = QTextBrowser()
        if self.current_language == 'ru':
            dialog.setWindowTitle("О программе")
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
        else:
            dialog.setWindowTitle("About the program")
            text_browser.setHtml("""
                <div style='text-align: center;'>
                    <h1>Text editor</h1>
                    <p style='color: #868e94; font-size: 14px;'>Version 1.0</p>

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
