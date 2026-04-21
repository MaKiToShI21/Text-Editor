from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerCPP


class CustomCppLexer(QsciLexerCPP):
    def keywords(self, keyset):
        if keyset == 2:
            return "std complex"
        return super().keywords(keyset)


class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Line numbering
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
        self.setMarginsForegroundColor(QColor(160, 160, 160))
        self.setMarginsBackgroundColor(QColor(45, 45, 45))

        # Font setting
        current_font = self.font()
        bold_font = QFont(current_font)
        bold_font.setBold(True)
        self.setMarginsFont(bold_font)

        # Dynamically changing the width of the numbering field
        self.linesChanged.connect(self.update_line_number_width)
        self.update_line_number_width()

        # Syntax highlighting
        lexer = CustomCppLexer()
        editor_font = QFont("Consolas", 11)
        editor_font.setBold(True)
        lexer.setDefaultFont(editor_font)
        for style in range(128):
            lexer.setFont(editor_font, style)

        lexer.setColor(QColor(255, 255, 255), 0)
        lexer.setColor(QColor(9, 155, 0), 1)
        lexer.setColor(QColor(9, 155, 0), 2)
        lexer.setColor(QColor(122, 191, 124), 4)
        lexer.setColor(QColor(255, 80, 175), 5)
        lexer.setColor(QColor(255, 166, 74), 6)
        lexer.setColor(QColor(255, 166, 74), 7)
        lexer.setColor(QColor(207, 90, 230), 9)
        lexer.setColor(QColor(255, 255, 255), 10)
        lexer.setColor(QColor(255, 255, 255), 11)
        lexer.setColor(QColor(255, 166, 74), 12)
        lexer.setColor(QColor(150, 220, 255), 16)

        # Background
        lexer.setDefaultPaper(QColor("#242424"))
        lexer.setPaper(QColor("#242424"))

        # Text selection
        self.setSelectionBackgroundColor(QColor(190, 201, 58, 90))

        self.resetSelectionForegroundColor()

        # Cursor
        self.setCaretForegroundColor(QColor(255, 255, 255))
        self.setCaretWidth(2)

        # Highlighting
        self.setLexer(lexer)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor(45, 45, 45))  # Line highlighting

    def update_line_number_width(self):
        lines = self.lines()
        if lines < 100:
            self.setMarginWidth(0, "000")
        elif lines < 1000:
            self.setMarginWidth(0, "0000")
        elif lines < 10000:
            self.setMarginWidth(0, "00000")
        elif lines < 100000:
            self.setMarginWidth(0, "000000")
        else:
            self.setMarginWidth(0, "0000000")
