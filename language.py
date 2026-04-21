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
                'actionRunParser_toolTip': 'Синтаксический анализ',
                'actionRunLexer_toolTip': 'Лексический анализ',
                'actionSemanticAnalysis_toolTip': 'Семантический анализ',
                'actionOpenAST_toolTip': 'Построить AST',
                'actionUndo_toolTip': 'Отменить',
                'actionRedo_toolTip': 'Повторить',
                'actionCut_toolTip': 'Вырезать',
                'actionCopy_toolTip': 'Копировать',
                'actionPaste_toolTip': 'Вставить',
                'actionDelete_toolTip': 'Удалить',
                'actionSelectAll_toolTip': 'Выделить всё',

                # Text menu actions
                'actionOpenProblemStatement': 'Постановка задачи',
                'actionOpenStateDiagram': 'Диаграмма состояний',
                'actionOpenGrammar': 'Грамматика',
                'actionOpenGrammarClass': 'Классификация грамматики',
                'actionOpenAnalysisMethod': 'Метод анализа',
                'actionDiagnosticsTroubleshooting': 'Диагностика и нейтрализация ошибок',
                'actionOpenExample': 'Тестовый пример',
                'actionOpenReferences': 'Список литературы',
                'actionOpenSourceCode': 'Исходный код программы',

                # Run menu actions
                'actionRunParser': 'Синтаксический анализ',
                'actionRunLexer': 'Лексический анализ',
                'actionSemanticAnalysis': 'Семантический анализ',
                'actionOpenAST': 'Построить AST',

                # Help menu actions
                'actionHelp': 'Вызов справки',
                'actionAbout': 'О программе',

                # Settings menu actions
                'actionLanguage': 'Смена языка',

                # Default tab titles
                'new_document': 'Новый документ',

                # Status bar
                # File actions
                'file_opened': 'Файл "{}" открыт',
                'opened_files': 'Открыто файлов: {}',

                'file_saved': 'Файл "{}" сохранён',
                'file_saved_as': 'Файл сохранён как "{}"',

                'save_cancelled': 'Сохранение отменено',

                'total_errors': 'Количество ошибок: {}',
                'no_errors': 'Ошибок нет',
                'parser_input_empty': 'Введите текст перед запуском синтаксического анализатора',
                'lexer_input_empty': 'Введите текст перед запуском лексического анализатора',
                'semantic_analysis_input_empty': 'Введите текст перед запуском семантического анализатора',

                'actionUndo_status_bar': 'Действие отменено',
                'actionRedo_status_bar': 'Действие повторено',
                'actionCut_status_bar': 'Текст вырезан',
                'actionCopy_status_bar': 'Текст скопирован',
                'actionPaste_status_bar': 'Текст вставлен',
                'actionDelete_status_bar': 'Текст удалён',
                'actionSelectAll_status_bar': 'Весь текст выделен',

                'copied': 'Текст скопирован',
                'pasted': 'Текст вставлен',
                'cut': 'Текст вырезан',
                'deleted': 'Текст удалён',
                'selected_all': 'Весь текст выделен',
                'undo': 'Действие отменено',
                'redo': 'Действие повторено',
                'language_changed': 'Язык изменён на русский',
                'lang_not_changed': 'Язык не был изменён',
                'lang_selection_cancelled': 'Выбор языка отменён',

                # Tab actions
                'tab_saved_and_closed': 'Вкладка "{}" сохранена и закрыта',
                'tab_closed_without_saving': 'Вкладка "{}" закрыта без сохранения',
                'tab_closed': 'Вкладка "{}" закрыта',
                'tab_closing_cancelled': 'Закрытие вкладки "{}" отменено',

                'text_edit_inactive': 'Текстовое поле не активно',

                # Drag and drop action
                'drop_hint': 'Отпустите файл для открытия',

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
                'expected': 'Ожидалось: {}',

                # For lexer
                'kw_double': 'Ключевое слово double',
                'kw_std': 'Ключевое слово std',
                'kw_complex': 'Ключевое слово complex',
                'identifier': 'Идентификатор',
                'space': 'Пробел',
                'integer': 'Целое число',
                'float': 'Число с плавающей точкой',
                'double_colon': 'Двойное двоеточие',
                'open_angle': 'Открывающая угловая скобка',
                'close_angle': 'Закрывающая угловая скобка',
                'open_paren': 'Открывающая круглая скобка',
                'close_paren': 'Закрывающая круглая скобка',
                'minus': 'Минус',
                'comma': 'Запятая',
                'semicolon': 'Точка с запятой',
                'invalid_char': 'Недопустимый фрагмент',
                'unknown_code': 'Неизвестный код {}',
                'line_num': 'Строка {}',
                'cond_code': 'Условный код',
                'lexeme_type': 'Тип лексемы',
                'lexeme': 'Лексема',
                'location': 'Местоположение',
                'parser_wrong_fragment': 'Неверный фрагмент',
                'parser_error_description': 'Описание ошибки',
                'output_tab_result': 'Результат',
                'output_tab_errors': 'Ошибки',
                'output_tab_ast': 'AST',
                'ast_not_available': 'AST пока не построено',
                'semantic_message': 'Сообщение',
                'semantic_position': 'Позиция',
                'semantic_duplicate_identifier': 'Ошибка: идентификатор "{}" уже объявлен ранее (строка {})',
                'semantic_type_mismatch': 'Ошибка: значение "{}" имеет тип int, ожидался double',
                'semantic_out_of_range': 'Ошибка: значение "{}" вне диапазона типа double'
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
                'actionRunParser_toolTip': 'Syntactic analysis',
                'actionRunLexer_toolTip': 'Lexical analysis',
                'actionSemanticAnalysis_toolTip': 'Semantic analysis',
                'actionOpenAST_toolTip': 'Build AST',
                'actionUndo_toolTip': 'Undo',
                'actionRedo_toolTip': 'Redo',
                'actionCut_toolTip': 'Cut',
                'actionCopy_toolTip': 'Copy',
                'actionPaste_toolTip': 'Paste',
                'actionDelete_toolTip': 'Delete',
                'actionSelectAll_toolTip': 'Select all',

                # Text menu actions
                'actionOpenProblemStatement': 'Problem statement',
                'actionOpenStateDiagram': 'State diagram',
                'actionOpenGrammar': 'Grammar',
                'actionOpenGrammarClass': 'Grammar classification',
                'actionOpenAnalysisMethod': 'Analysis method',
                'actionDiagnosticsTroubleshooting': 'Diagnostics and troubleshooting',
                'actionOpenExample': 'Test example',
                'actionOpenReferences': 'References',
                'actionOpenSourceCode': 'Source code',

                # Run menu actions
                'actionRunParser': 'Syntactic analysis',
                'actionRunLexer': 'Lexical analysis',
                'actionSemanticAnalysis': 'Semantic analysis',
                'actionOpenAST': 'Build AST',

                # Help menu actions
                'actionHelp': 'Help',
                'actionAbout': 'About',

                # Settings menu actions
                'actionLanguage': 'Change language',

                # Default tab titles
                'new_document': 'New Document',

                # Status bar
                # File actions
                'file_opened': 'File "{}" opened',
                'opened_files': 'Opened files: {}',

                'file_saved': 'File "{}" saved',
                'file_saved_as': 'File saved as "{}"',

                'save_cancelled': 'Save cancelled',

                'total_errors': 'Number of errors: {}',
                'no_errors': 'No errors',
                'parser_input_empty': 'Enter text before running the parser',
                'lexer_input_empty': 'Enter text before running the lexical analyzer',
                'semantic_analysis_input_empty': 'Enter text before running the semantic analyzer',

                'actionUndo_status_bar': 'Action undone',
                'actionRedo_status_bar': 'Action redone',
                'actionCut_status_bar': 'Text cut',
                'actionCopy_status_bar': 'Text copied',
                'actionPaste_status_bar': 'Text pasted',
                'actionDelete_status_bar': 'Text deleted',
                'actionSelectAll_status_bar': 'All text selected',

                'copied': 'Text copied',
                'pasted': 'Text pasted',
                'cut': 'Text cut',
                'deleted': 'Text deleted',
                'selected_all': 'All text selected',
                'undo': 'Action undone',
                'redo': 'Action redone',
                'language_changed': 'Language changed to English',
                'lang_not_changed': 'Language not changed',
                'lang_selection_cancelled': 'Language selection canceled',

                # Tab actions
                'tab_saved_and_closed': 'Tab "{}" saved and closed',
                'tab_closed_without_saving': 'Tab "{}" closed without saving',
                'tab_closed': 'Tab "{}" closed',
                'tab_closing_cancelled': 'Tab close "{}" cancelled',

                'text_edit_inactive': 'Text edit not active',

                # Drag and drop action
                'drop_hint': 'Drop files to open',

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
                'expected': 'Expected: {}',

                # For lexer
                'kw_double': 'Keyword double',
                'kw_std': 'Keyword std',
                'kw_complex': 'Keyword complex',
                'identifier': 'Identifier',
                'space': 'Space',
                'integer': 'Integer',
                'float': 'Floating point number',
                'double_colon': 'Double colon',
                'open_angle': 'Opening angle bracket',
                'close_angle': 'Closing angle bracket',
                'open_paren': 'Opening parenthesis',
                'close_paren': 'Closing parenthesis',
                'minus': 'Minus',
                'comma': 'Comma',
                'semicolon': 'Semicolon',
                'invalid_char': 'Invalid fragment',
                'line_num': 'Line {}',
                'cond_code': 'Conditional code',
                'lexeme_type': 'Lexeme type',
                'lexeme': 'Lexeme',
                'location': 'Location',
                'parser_wrong_fragment': 'Wrong fragment',
                'parser_error_description': 'Error description',
                'output_tab_result': 'Result',
                'output_tab_errors': 'Errors',
                'output_tab_ast': 'AST',
                'ast_not_available': 'AST is not built yet',
                'semantic_message': 'Message',
                'semantic_position': 'Position',
                'semantic_duplicate_identifier': 'Error: identifier "{}" was already declared before (line {})',
                'semantic_type_mismatch': 'Error: value "{}" has int type, expected double',
                'semantic_out_of_range': 'Error: value "{}" is out of range for double'
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
        title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title_label)

        self.radio_group = QButtonGroup(self)

        self.rb_russian = QRadioButton("Русский")
        self.rb_russian.setChecked(lang.current_language == 'ru')
        self.rb_russian.toggled.connect(lambda: self.set_language('ru'))
        self.rb_russian.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.rb_russian)
        self.radio_group.addButton(self.rb_russian)

        self.rb_english = QRadioButton("English")
        self.rb_english.setChecked(lang.current_language == 'en')
        self.rb_english.toggled.connect(lambda: self.set_language('en'))
        self.rb_english.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.rb_english)
        self.radio_group.addButton(self.rb_english)

        layout.addStretch()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("QPushButton { color: #ffffff; }")
        layout.addWidget(button_box)

    def set_language(self, lang):
        self.selected_language = lang

    def get_selected_language(self):
        return self.selected_language
