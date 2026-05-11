from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from lexer import LexicalAnalyzer
from optimizer import render_tac, run_optimization_pipeline
from parser import Parser
from semantic_analyzer import SemanticAnalyzer


class FullAnalysisWindow(QDialog):
    BLOCK_TITLE_STYLE = (
        "QGroupBox { color: #e0e0e0; font-weight: bold; "
        "border: 1px solid #404040; border-radius: 6px; "
        "margin-top: 10px; padding: 8px; } "
        "QGroupBox::title { subcontrol-origin: margin; left: 12px; "
        "padding: 0 5px 0 5px; }"
    )
    MONO_STYLE = (
        "background-color: #1f1f1f; color: #ffffff; "
        "border: 1px solid #303030; border-radius: 4px; padding: 6px;"
    )

    def __init__(self, lang, source_text: str, parent=None):
        super().__init__(parent)
        self.lang = lang
        self.setWindowTitle(self.lang.translate("full_analysis_title"))
        self.setMinimumSize(960, 720)
        self.resize(1180, 820)
        self.setStyleSheet("background-color: rgb(40, 40, 40);")

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        outer_layout.setSpacing(8)

        header = QLabel(self.lang.translate("full_analysis_description"))
        header.setWordWrap(True)
        header.setStyleSheet("color: #d0d0d0; padding: 6px 4px;")
        outer_layout.addWidget(header)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(
            "QScrollArea { background-color: rgb(40, 40, 40); border: none; }"
            "QScrollBar:vertical { background: #2d2d2d; width: 12px; }"
            "QScrollBar::handle:vertical { background: #555; border-radius: 5px; }"
        )

        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: rgb(40, 40, 40);")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(4, 4, 4, 4)
        self.content_layout.setSpacing(10)

        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area, stretch=1)

        button_row = QHBoxLayout()
        button_row.addStretch()
        close_button = QPushButton(self.lang.translate("close_button"))
        close_button.setStyleSheet(
            "QPushButton { color: #ffffff; background-color: rgb(70, 70, 70); "
            "padding: 6px 18px; border-radius: 5px; } "
            "QPushButton:hover { background-color: rgb(95, 95, 95); }"
        )
        close_button.clicked.connect(self.accept)
        button_row.addWidget(close_button)
        outer_layout.addLayout(button_row)

        self._build_sections(source_text)

    # Построение секций
    def _build_sections(self, source_text: str) -> None:
        if not source_text or not source_text.strip():
            self._add_message_section(self.lang.translate("full_analysis_no_input"))
            return

        self._add_source_section(source_text)

        lexer = LexicalAnalyzer(self.lang)
        tokens, lex_errors = lexer.analyze(source_text)
        self._add_lexer_section(tokens, lex_errors)

        parser = Parser(self.lang)
        _, syntax_errors = parser.parse(source_text)
        self._add_parser_section(syntax_errors)

        analyzer = SemanticAnalyzer(self.lang)
        semantic_errors, ast_text = analyzer.analyze(source_text)
        self._add_semantic_section(semantic_errors)

        non_empty_lines = [line for line in source_text.splitlines() if line.strip()]
        if not non_empty_lines:
            return

        has_blocking_errors = bool(syntax_errors) or bool(semantic_errors) or bool(lex_errors)
        if has_blocking_errors:
            self._add_message_section(
                self.lang.translate("full_analysis_blocked_by_errors")
            )
            return

        for index, line in enumerate(non_empty_lines, start=1):
            pipeline = run_optimization_pipeline(line)
            if pipeline is None:
                continue
            self._add_pipeline_section(index, line, pipeline)

    def _add_source_section(self, source_text: str) -> None:
        body = QPlainTextEdit()
        body.setPlainText(source_text)
        body.setReadOnly(True)
        body.setFont(QFont("Consolas", 10))
        body.setStyleSheet(self.MONO_STYLE)
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        body.setFixedHeight(min(180, max(60, 22 * (source_text.count("\n") + 2))))

        self._add_group(self.lang.translate("full_analysis_input_label"), body)

    def _add_lexer_section(self, tokens, errors) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        status = self._make_status_label(
            errors,
            ok_key="full_analysis_lexer_ok",
            err_key="full_analysis_lexer_errors",
        )
        layout.addWidget(status)

        table = self._make_token_table(tokens, errors)
        layout.addWidget(table)

        self._add_group(self.lang.translate("full_analysis_lexer_title"), container)

    def _add_parser_section(self, syntax_errors) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        status = self._make_status_label(
            syntax_errors,
            ok_key="full_analysis_parser_ok",
            err_key="full_analysis_parser_errors",
        )
        layout.addWidget(status)

        if syntax_errors:
            errors_table = self._make_errors_table(syntax_errors, kind_key="syntax_kind")
            layout.addWidget(errors_table)

        self._add_group(self.lang.translate("full_analysis_parser_title"), container)

    def _add_semantic_section(self, semantic_errors) -> None:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        status = self._make_status_label(
            semantic_errors,
            ok_key="full_analysis_semantic_ok",
            err_key="full_analysis_semantic_errors",
        )
        layout.addWidget(status)

        if semantic_errors:
            errors_table = self._make_errors_table(
                semantic_errors, kind_key="semantic_kind"
            )
            layout.addWidget(errors_table)

        self._add_group(
            self.lang.translate("full_analysis_semantic_title"),
            container,
        )

    def _add_pipeline_section(self, index, source_line, pipeline) -> None:
        title_template = self.lang.translate("full_analysis_pipeline_title")
        title = title_template.format(index=index, line=source_line.strip())

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._make_subsection(
            self.lang.translate("full_analysis_ast_label"),
            pipeline.ast_text,
        ))

        layout.addWidget(self._make_subsection(
            self.lang.translate("full_analysis_initial_ir_label"),
            render_tac(pipeline.initial_tac),
            description=self.lang.translate("full_analysis_initial_ir_desc"),
        ))

        layout.addWidget(self._make_optimization_block(
            self.lang.translate("full_analysis_opt1_title"),
            self.lang.translate("full_analysis_opt1_desc"),
            render_tac(pipeline.initial_tac),
            render_tac(pipeline.after_constant_folding),
        ))

        layout.addWidget(self._make_optimization_block(
            self.lang.translate("full_analysis_opt2_title"),
            self.lang.translate("full_analysis_opt2_desc"),
            render_tac(pipeline.after_constant_folding),
            render_tac(pipeline.after_copy_propagation),
        ))

        self._add_group(title, container)

    # Вспомогательные виджеты
    def _add_group(self, title: str, content_widget: QWidget) -> None:
        group = QGroupBox(title)
        group.setStyleSheet(self.BLOCK_TITLE_STYLE)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(10, 16, 10, 10)
        layout.addWidget(content_widget)
        self.content_layout.addWidget(group)

    def _add_message_section(self, message: str) -> None:
        label = QLabel(message)
        label.setWordWrap(True)
        label.setStyleSheet(
            "color: #f0a040; padding: 6px; background-color: #2a2a2a; "
            "border: 1px solid #444; border-radius: 4px;"
        )
        self.content_layout.addWidget(label)

    def _make_status_label(self, errors, ok_key: str, err_key: str) -> QLabel:
        if not errors:
            text = self.lang.translate(ok_key)
            color = "#7bd07b"
        else:
            text = self.lang.translate(err_key).format(len(errors))
            color = "#e07070"
        label = QLabel(text)
        label.setStyleSheet(f"color: {color}; font-weight: bold; padding: 2px;")
        return label

    def _make_token_table(self, tokens, errors) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            [
                self.lang.translate("cond_code"),
                self.lang.translate("lexeme_type"),
                self.lang.translate("lexeme"),
                self.lang.translate("location"),
            ]
        )

        rows = [(item, "error") for item in errors] + [(item, "token") for item in tokens]
        table.setRowCount(len(rows))
        for row, (item, kind) in enumerate(rows):
            code_value = item.get("code", "")
            type_value = item.get("type", "")
            lexeme = item.get("lexeme", "")
            location = item.get("location", "")
            colour = Qt.GlobalColor.red if kind == "error" else Qt.GlobalColor.white
            for col, value in enumerate([str(code_value), type_value, lexeme, location]):
                cell = QTableWidgetItem(value)
                cell.setForeground(colour)
                table.setItem(row, col, cell)

        self._tune_table(table)
        return table

    def _make_errors_table(self, errors, kind_key: str) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(
            [
                self.lang.translate("parser_wrong_fragment"),
                self.lang.translate("analysis_type"),
                self.lang.translate("parser_error_description"),
                self.lang.translate("location"),
            ]
        )
        table.setRowCount(len(errors))
        kind_text = self.lang.translate(kind_key)
        for row, error in enumerate(errors):
            lexeme = error.get("lexeme", "")
            description = error.get("description", error.get("type", ""))
            location = error.get("location", "")
            for col, value in enumerate([lexeme, kind_text, description, location]):
                cell = QTableWidgetItem(value)
                cell.setForeground(Qt.GlobalColor.red)
                table.setItem(row, col, cell)
        self._tune_table(table)
        return table

    @staticmethod
    def _tune_table(table: QTableWidget) -> None:
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        vertical_header = table.verticalHeader()
        if vertical_header is not None:
            vertical_header.setVisible(True)
        header = table.horizontalHeader()
        header_height = 28
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setStretchLastSection(True)
            header.setStyleSheet(
                "QHeaderView::section { background-color: #303030; "
                "color: #ffffff; padding: 4px; border: 1px solid #404040; }"
            )
            header_height = header.height() or header_height
        table.setStyleSheet(
            "QTableWidget { background-color: #1f1f1f; gridline-color: #353535; }"
        )
        rows_to_show = min(max(table.rowCount(), 1), 8)
        row_height = 24
        if vertical_header is not None:
            row_height = vertical_header.defaultSectionSize() or row_height
        table.setFixedHeight(row_height * rows_to_show + header_height + 4)

    def _make_subsection(self, label_text: str, body_text: str, description: str | None = None) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        label = QLabel(label_text)
        label.setStyleSheet("color: #d0d0d0; font-weight: bold;")
        layout.addWidget(label)

        if description:
            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #a0a0a0; font-style: italic;")
            layout.addWidget(desc_label)

        body = QPlainTextEdit()
        body.setPlainText(body_text or "<empty>")
        body.setReadOnly(True)
        body.setFont(QFont("Consolas", 10))
        body.setStyleSheet(self.MONO_STYLE)
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        lines_count = (body_text or "").count("\n") + 2
        body.setFixedHeight(min(280, max(70, 20 * lines_count)))
        layout.addWidget(body)
        return container

    def _make_optimization_block(
        self,
        title: str,
        description: str,
        input_ir: str,
        output_ir: str,
    ) -> QWidget:
        container = QGroupBox(title)
        container.setStyleSheet(
            "QGroupBox { color: #f0c060; font-weight: bold; "
            "border: 1px solid #555; border-radius: 4px; "
            "margin-top: 8px; padding: 6px; } "
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px 0 4px; }"
        )
        outer = QVBoxLayout(container)
        outer.setContentsMargins(10, 14, 10, 10)
        outer.setSpacing(6)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #d0d0d0;")
        outer.addWidget(desc_label)

        columns = QHBoxLayout()
        columns.setSpacing(8)

        in_widget = self._make_io_panel(
            self.lang.translate("full_analysis_input_ir_label"),
            input_ir,
        )
        out_widget = self._make_io_panel(
            self.lang.translate("full_analysis_output_ir_label"),
            output_ir,
        )
        columns.addWidget(in_widget, 1)
        columns.addWidget(out_widget, 1)
        outer.addLayout(columns)
        return container

    def _make_io_panel(self, label_text: str, body_text: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(label_text)
        label.setStyleSheet("color: #c0c0c0; font-weight: bold;")
        layout.addWidget(label)

        body = QTextEdit()
        body.setPlainText(body_text or "<empty>")
        body.setReadOnly(True)
        body.setFont(QFont("Consolas", 10))
        body.setStyleSheet(self.MONO_STYLE)
        lines_count = (body_text or "").count("\n") + 2
        body.setFixedHeight(min(260, max(60, 20 * lines_count)))
        body.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(body)
        return container
