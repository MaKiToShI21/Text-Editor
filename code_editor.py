from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerPython


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
        lexer = QsciLexerPython()
        lexer.setColor(QColor(9, 145, 0), 1)    # Comments with #
        lexer.setColor(QColor(122, 191, 124), 2)   # Numbers
        lexer.setColor(QColor(190, 90, 55), 3)    # Quoted strings with ""
        lexer.setColor(QColor(180, 90, 51), 4)   # Strings in quotes with ''
        lexer.setColor(QColor(43, 150, 214), 5)   # Keywords: def, class, if, else
        lexer.setColor(QColor(180, 90, 51), 6)   # Block comments with ''' '''
        lexer.setColor(QColor(0, 210, 180), 8)  # Class names
        lexer.setColor(QColor(205, 209, 100), 9)   # Name of functions
        lexer.setColor(QColor(190, 90, 55), 13)  # Quoted strings with ", '
        lexer.setColor(QColor(205, 209, 100), 15)  # Decorators @staticmethod
        lexer.setColor(QColor(180, 90, 51), 17)  # f'{}'

        # Background
        lexer.setDefaultPaper(QColor("#242424"))
        lexer.setPaper(QColor("#242424"))

        # Text selection
        self.setSelectionBackgroundColor(QColor(0, 100, 200, 60))
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
