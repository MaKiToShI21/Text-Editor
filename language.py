from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QRadioButton,
                             QDialogButtonBox, QButtonGroup)
from PyQt6.QtCore import Qt


class Language():
    def __init__(self):
        # Dictionary with translations
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

                # Action tooltips
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

                # Status bar
                # File actions
                'file_opened': 'Файл "{}" открыт',
                'opened_files': 'Открыто файлов: {}',

                'file_saved': 'Файл "{}" сохранён',
                'file_saved_as': 'Файл сохранён как "{}"',

                'save_cancelled': 'Сохранение отменено',

                # Tab actions
                'tab_saved_and_closed': 'Вкладка "{}" сохранена и закрыта',
                'tab_closed_without_saving': 'Вкладка "{}" закрыта без сохранения',
                'tab_closing_cancelled': 'Закрытие вкладки "{}" отменено',

                'text_edit_inactive': 'Текстовое поле не активно',

                # Drag and drop action
                'drop_hint': 'Отпустите файл для открытия',

                # Tool bar actions
                'copied': 'Скопировано',
                'pasted': 'Вставлено',
                'cut': 'Вырезано',
                'deleted': 'Удалено',
                'selected_all': 'Выделено всё',
                'undo': 'Отмена',
                'redo': 'Повтор',
                'language_changed': 'Язык изменён на русский',
                'lang_not_changed': 'Язык не был изменён',
                'lang_selection_cancelled': 'Выбор языка отменён',

                # Dialog windows
                # Titles
                'language_selection': 'Выбор языка',
                'actionSaveFileAs': 'Сохранить файл как',
                'choose_file_to_open': 'Выберите файл для открытия',
                'unsaved_changes': 'Несохранённые изменения',

                # Texts
                'select_interface_lang': 'Выберите язык интерфейса',
                'save_changes': 'Сохранить изменения в "{}"?',

                # Error messages
                'error': 'Ошибка',
                'opening_error': 'Не удалось открыть файл:\n{}',
                'file_saving_error': 'Не удалось сохранить файл: {}',
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

                # Status bar
                # File actions
                'file_opened': 'File "{}" opened',
                'opened_files': 'Opened files: {}',

                'file_saved': 'File "{}" saved',
                'file_saved_as': 'File saved as "{}"',

                'save_cancelled': 'Save cancelled',

                # Tab actions
                'tab_saved_and_closed': 'Tab "{}" saved and closed',
                'tab_closed_without_saving': 'Tab "{}" closed without saving',
                'tab_closing_cancelled': 'Tab close "{}" cancelled',

                'text_edit_inactive': 'Text edit not active',

                # Drag and drop action
                'drop_hint': 'Drop files to open',

                # Tool bar actions
                'copied': 'Copied',
                'pasted': 'Pasted',
                'cut': 'Cut',
                'deleted': 'Deleted',
                'selected_all': 'Selected all',
                'undo': 'Undo',
                'redo': 'Redo',
                'language_changed': 'Language changed to English',
                'lang_not_changed': 'The language has not been changed',
                'lang_selection_cancelled': 'Language selection cancelled',

                # Dialog windows
                # Titles
                'language_selection': 'Language selection',
                'actionSaveFileAs': 'Save file as',
                'choose_file_to_open': 'Choose file to open',
                'unsaved_changes': 'Unsaved Changes',

                # Texts
                'select_interface_lang': 'Select the interface language',
                'save_changes': 'Save changes in "{}"?',

                # Error messages
                'error': 'Error',
                'opening_error': 'Could not open file:\n{}',
                'file_saving_error': 'Failed to save file: {}',
            }
        }

        self.current_language = 'ru'
        self.load_language_setting()

    def translate(self, key):
        return self.translations[self.current_language].get(key, key)

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

                if self.current_language not in ['ru', 'en']:
                    self.current_language = 'ru'
                    self.save_language_setting()
        except:
            pass


class LanguageDialog(QDialog):
    def __init__(self, lang, parent=None):
        super().__init__(parent)

        self.selected_language = lang.current_language

        self.setWindowTitle(lang.translate('language_selection'))
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        title_label = QLabel(lang.translate('select_interface_lang'))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title_label)

        self.radio_group = QButtonGroup(self)

        self.rb_russian = QRadioButton("Русский")
        self.rb_russian.setChecked(lang.current_language == 'ru')
        self.rb_russian.toggled.connect(lambda: self.set_language('ru'))
        layout.addWidget(self.rb_russian)
        self.radio_group.addButton(self.rb_russian)

        self.rb_english = QRadioButton("English")
        self.rb_english.setChecked(lang.current_language == 'en')
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
