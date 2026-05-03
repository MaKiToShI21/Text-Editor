from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QRadioButton,
    QVBoxLayout,
)


class Language:
    def __init__(self):
        self.translations = {
            "ru": {
                "window_title": "Текстовый редактор",
                "menuFile": "Файл",
                "menuEdit": "Правка",
                "menuText": "Текст",
                "menuRun": "Запуск",
                "menuHelp": "Справка",
                "menuSettings": "Настройки",
                "actionNew": "Создать",
                "actionOpen": "Открыть",
                "actionSave": "Сохранить",
                "actionSaveAs": "Сохранить как",
                "actionExit": "Выход",
                "actionUndo": "Отменить",
                "actionRedo": "Повторить",
                "actionCut": "Вырезать",
                "actionCopy": "Копировать",
                "actionPaste": "Вставить",
                "actionDelete": "Удалить",
                "actionSelectAll": "Выделить всё",
                "actionOpenProblemStatement": "Постановка задачи",
                "actionOpenStateDiagram": "Диаграмма состояний",
                "actionOpenGrammar": "Грамматика",
                "actionOpenGrammarClass": "Классификация грамматики",
                "actionOpenAnalysisMethod": "Метод анализа",
                "actionDiagnosticsTroubleshooting": "Диагностика и нейтрализация ошибок",
                "actionOpenExample": "Тестовый пример",
                "actionOpenReferences": "Список литературы",
                "actionOpenSourceCode": "Исходный код программы",
                "actionRunLexer": "Лексический анализ",
                "actionRunParser": "Разбор и внутреннее представление",
                "actionHelp": "Справка",
                "actionAbout": "О программе",
                "actionLanguage": "Сменить язык",
                "actionNew_toolTip": "Создать",
                "actionOpen_toolTip": "Открыть",
                "actionSave_toolTip": "Сохранить",
                "actionSaveAs_toolTip": "Сохранить как",
                "actionExit_toolTip": "Выход",
                "actionUndo_toolTip": "Отменить",
                "actionRedo_toolTip": "Повторить",
                "actionCut_toolTip": "Вырезать",
                "actionCopy_toolTip": "Копировать",
                "actionPaste_toolTip": "Вставить",
                "actionDelete_toolTip": "Удалить",
                "actionSelectAll_toolTip": "Выделить всё",
                "actionRunLexer_toolTip": "Лексический анализ",
                "actionRunParser_toolTip": "Лексический и синтаксический анализ, тетрады и ПОЛИЗ",
                "new_document": "Новый документ",
                "file_opened": "Файл \"{}\" открыт",
                "opened_files": "Открыто файлов: {}",
                "file_saved": "Файл \"{}\" сохранён",
                "file_saved_as": "Файл сохранён как \"{}\"",
                "save_cancelled": "Сохранение отменено",
                "total_errors": "Количество ошибок: {}",
                "no_errors": "Ошибок нет",
                "parser_input_empty": "Введите текст перед запуском синтаксического анализатора",
                "lexer_input_empty": "Введите текст перед запуском лексического анализатора",
                "actionUndo_status_bar": "Действие отменено",
                "actionRedo_status_bar": "Действие повторено",
                "actionCut_status_bar": "Текст вырезан",
                "actionCopy_status_bar": "Текст скопирован",
                "actionPaste_status_bar": "Текст вставлен",
                "actionDelete_status_bar": "Текст удалён",
                "actionSelectAll_status_bar": "Весь текст выделен",
                "language_changed": "Язык изменён на русский",
                "lang_not_changed": "Язык не изменён",
                "lang_selection_cancelled": "Выбор языка отменён",
                "tab_saved_and_closed": "Вкладка \"{}\" сохранена и закрыта",
                "tab_closed_without_saving": "Вкладка \"{}\" закрыта без сохранения",
                "tab_closed": "Вкладка \"{}\" закрыта",
                "tab_closing_cancelled": "Закрытие вкладки \"{}\" отменено",
                "text_edit_inactive": "Текстовое поле неактивно",
                "drop_hint": "Отпустите файл для открытия",
                "language_selection": "Выбор языка",
                "actionSaveFileAs": "Сохранить файл как",
                "choose_file_to_open": "Выберите файл для открытия",
                "unsaved_changes": "Несохранённые изменения",
                "select_interface_lang": "Выберите язык интерфейса",
                "save_changes": "Сохранить изменения в \"{}\"?",
                "error": "Ошибка",
                "opening_error": "Не удалось открыть файл:\n{}",
                "file_saving_error": "Не удалось сохранить файл: {}",
                "identifier": "Идентификатор",
                "integer": "Целое число",
                "float": "Число с плавающей точкой",
                "plus": "Плюс",
                "minus": "Минус",
                "multiply": "Умножение",
                "divide": "Деление",
                "module": "Остаток от деления (%)",
                "open_paren": "Открывающая круглая скобка",
                "close_paren": "Закрывающая круглая скобка",
                "space": "Пробел",
                "invalid_char": "Недопустимый фрагмент",
                "unknown_code": "Неизвестный код {}",
                "line_num": "Строка {}",
                "cond_code": "Условный код",
                "lexeme_type": "Тип лексемы",
                "lexeme": "Лексема",
                "location": "Местоположение",
                "parser_wrong_fragment": "Неверный фрагмент",
                "analysis_type": "Тип",
                "lexical_kind": "Лексическая",
                "syntax_kind": "Синтаксическая",
                "semantic_kind": "Семантическая",
                "parser_error_description": "Описание ошибки",
                "output_tab_result": "Результат",
                "output_tab_errors": "Ошибки",
                "parser_expected_operand": "Ожидался операнд: идентификатор, число или '('",
                "parser_expected_operator": "Ожидался оператор",
                "parser_expected_closing_paren": "Ожидалась закрывающая скобка ')'",
                "parser_unexpected_closing_paren": "Лишняя закрывающая скобка ')'",
                "parser_unexpected_token": "Неожиданный токен \"{}\"",
                "ir_line": "Строка",
                "ir_quadruples": "Тетрады",
                "ir_poliz": "ПОЛИЗ",
                "ir_value": "Значение",
                "no_quadruples": "Тетрады не требуются",
                "poliz_not_available": "ПОЛИЗ строится только для выражений из целых чисел",
                "division_by_zero": "Деление на ноль",
                "module_by_zero": "Делитель не может быть равен нулю",
                "ir_skipped_due_to_errors": "Обнаружены лексические или синтаксические ошибки: ВПП для некорректных строк не строится.",
                "ir_no_expressions": "Нет непустых строк с выражениями для построения ВПП.",
                "output_tab_ir": "Внутреннее представление",
                "ast_not_available": "Нет данных для отображения",
            },
            "en": {
                "window_title": "Text Editor",
                "menuFile": "File",
                "menuEdit": "Edit",
                "menuText": "Text",
                "menuRun": "Run",
                "menuHelp": "Help",
                "menuSettings": "Settings",
                "actionNew": "New",
                "actionOpen": "Open",
                "actionSave": "Save",
                "actionSaveAs": "Save As",
                "actionExit": "Exit",
                "actionUndo": "Undo",
                "actionRedo": "Redo",
                "actionCut": "Cut",
                "actionCopy": "Copy",
                "actionPaste": "Paste",
                "actionDelete": "Delete",
                "actionSelectAll": "Select All",
                "actionOpenProblemStatement": "Problem statement",
                "actionOpenStateDiagram": "State diagram",
                "actionOpenGrammar": "Grammar",
                "actionOpenGrammarClass": "Grammar classification",
                "actionOpenAnalysisMethod": "Analysis method",
                "actionDiagnosticsTroubleshooting": "Diagnostics and troubleshooting",
                "actionOpenExample": "Test example",
                "actionOpenReferences": "References",
                "actionOpenSourceCode": "Source code",
                "actionRunLexer": "Lexical analysis",
                "actionRunParser": "Syntactic analysis",
                "actionHelp": "Help",
                "actionAbout": "About",
                "actionLanguage": "Change language",
                "actionNew_toolTip": "Create",
                "actionOpen_toolTip": "Open",
                "actionSave_toolTip": "Save",
                "actionSaveAs_toolTip": "Save As",
                "actionExit_toolTip": "Exit",
                "actionUndo_toolTip": "Undo",
                "actionRedo_toolTip": "Redo",
                "actionCut_toolTip": "Cut",
                "actionCopy_toolTip": "Copy",
                "actionPaste_toolTip": "Paste",
                "actionDelete_toolTip": "Delete",
                "actionSelectAll_toolTip": "Select all",
                "actionRunLexer_toolTip": "Lexical analysis",
                "actionRunParser_toolTip": "Lexical/syntax analysis, quadruples and RPN",
                "new_document": "New Document",
                "file_opened": "File \"{}\" opened",
                "opened_files": "Opened files: {}",
                "file_saved": "File \"{}\" saved",
                "file_saved_as": "File saved as \"{}\"",
                "save_cancelled": "Save cancelled",
                "total_errors": "Number of errors: {}",
                "no_errors": "No errors",
                "parser_input_empty": "Enter text before running the parser",
                "lexer_input_empty": "Enter text before running the lexical analyzer",
                "actionUndo_status_bar": "Action undone",
                "actionRedo_status_bar": "Action redone",
                "actionCut_status_bar": "Text cut",
                "actionCopy_status_bar": "Text copied",
                "actionPaste_status_bar": "Text pasted",
                "actionDelete_status_bar": "Text deleted",
                "actionSelectAll_status_bar": "All text selected",
                "language_changed": "Language changed to English",
                "lang_not_changed": "Language not changed",
                "lang_selection_cancelled": "Language selection canceled",
                "tab_saved_and_closed": "Tab \"{}\" saved and closed",
                "tab_closed_without_saving": "Tab \"{}\" closed without saving",
                "tab_closed": "Tab \"{}\" closed",
                "tab_closing_cancelled": "Tab close \"{}\" cancelled",
                "text_edit_inactive": "Text edit not active",
                "drop_hint": "Drop files to open",
                "language_selection": "Language selection",
                "actionSaveFileAs": "Save file as",
                "choose_file_to_open": "Choose file to open",
                "unsaved_changes": "Unsaved Changes",
                "select_interface_lang": "Select the interface language",
                "save_changes": "Save changes in \"{}\"?",
                "error": "Error",
                "opening_error": "Could not open file:\n{}",
                "file_saving_error": "Failed to save file: {}",
                "identifier": "Identifier",
                "integer": "Integer",
                "float": "Floating point number",
                "plus": "Plus",
                "minus": "Minus",
                "multiply": "Multiplication",
                "divide": "Division",
                "module": "Module (%)",
                "open_paren": "Opening parenthesis",
                "close_paren": "Closing parenthesis",
                "space": "Space",
                "invalid_char": "Invalid fragment",
                "unknown_code": "Unknown code {}",
                "line_num": "Line {}",
                "cond_code": "Conditional code",
                "lexeme_type": "Lexeme type",
                "lexeme": "Lexeme",
                "location": "Location",
                "parser_wrong_fragment": "Wrong fragment",
                "analysis_type": "Type",
                "lexical_kind": "Lexical",
                "syntax_kind": "Syntax",
                "semantic_kind": "Semantic",
                "parser_error_description": "Error description",
                "output_tab_result": "Result",
                "output_tab_errors": "Errors",
                "parser_expected_operand": "Expected operand: identifier, number, or '('",
                "parser_expected_operator": "Expected operator",
                "parser_expected_closing_paren": "Expected closing parenthesis ')'",
                "parser_unexpected_closing_paren": "Unexpected closing parenthesis ')'",
                "parser_unexpected_token": "Unexpected token \"{}\"",
                "ir_line": "Line",
                "ir_quadruples": "Quadruples",
                "ir_poliz": "RPN",
                "ir_value": "Value",
                "no_quadruples": "No quadruples required",
                "poliz_not_available": "RPN is only built for integer-only expressions",
                "division_by_zero": "Division by zero",
                "module_by_zero": "Module by zero",
                "ir_skipped_due_to_errors": "Lexical or syntax errors present: IR is not built for invalid lines.",
                "ir_no_expressions": "No non-empty expression lines to build IR from.",
                "output_tab_ir": "Intermediate representation",
                "ast_not_available": "Nothing to display",
            },
        }

        self.current_language = "ru"
        self.load_language_setting()

    def translate(self, key):
        return self.translations[self.current_language].get(key, key)

    def save_language_setting(self):
        try:
            with open("language_config.txt", "w", encoding="utf-8") as file:
                file.write(self.current_language)
        except Exception:
            pass

    def load_language_setting(self):
        try:
            with open("language_config.txt", "r", encoding="utf-8") as file:
                loaded = file.read().strip()
                if loaded in {"ru", "en"}:
                    self.current_language = loaded
        except Exception:
            pass


class LanguageDialog(QDialog):
    def __init__(self, lang, parent=None):
        super().__init__(parent)

        self.selected_language = lang.current_language

        self.setWindowTitle(lang.translate("language_selection"))
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        title_label = QLabel(lang.translate("select_interface_lang"))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title_label)

        self.radio_group = QButtonGroup(self)

        self.rb_russian = QRadioButton("Русский")
        self.rb_russian.setChecked(lang.current_language == "ru")
        self.rb_russian.toggled.connect(lambda: self.set_language("ru"))
        self.rb_russian.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.rb_russian)
        self.radio_group.addButton(self.rb_russian)

        self.rb_english = QRadioButton("English")
        self.rb_english.setChecked(lang.current_language == "en")
        self.rb_english.toggled.connect(lambda: self.set_language("en"))
        self.rb_english.setStyleSheet("color: #ffffff;")
        layout.addWidget(self.rb_english)
        self.radio_group.addButton(self.rb_english)

        layout.addStretch()

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("QPushButton { color: #ffffff; }")
        layout.addWidget(button_box)

    def set_language(self, lang):
        self.selected_language = lang

    def get_selected_language(self):
        return self.selected_language
