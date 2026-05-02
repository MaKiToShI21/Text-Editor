class LexicalAnalyzer:
    TOKEN_CODES = {
        "IDENTIFIER": 1,
        "INTEGER": 2,
        "FLOAT": 3,
        "PLUS": 4,
        "MINUS": 5,
        "MULTIPLY": 6,
        "DIVIDE": 7,
        "MODULE": 8,
        "OPEN_PAREN": 9,
        "CLOSE_PAREN": 10,
        "SPACE": 11,
    }

    TOKEN_LABEL_KEYS = {
        TOKEN_CODES["IDENTIFIER"]: "identifier",
        TOKEN_CODES["INTEGER"]: "integer",
        TOKEN_CODES["FLOAT"]: "float",
        TOKEN_CODES["PLUS"]: "plus",
        TOKEN_CODES["MINUS"]: "minus",
        TOKEN_CODES["MULTIPLY"]: "multiply",
        TOKEN_CODES["DIVIDE"]: "divide",
        TOKEN_CODES["MODULE"]: "module",
        TOKEN_CODES["OPEN_PAREN"]: "open_paren",
        TOKEN_CODES["CLOSE_PAREN"]: "close_paren",
        TOKEN_CODES["SPACE"]: "space",
    }

    SINGLE_CHAR_TOKENS = {
        "+": TOKEN_CODES["PLUS"],
        "-": TOKEN_CODES["MINUS"],
        "*": TOKEN_CODES["MULTIPLY"],
        "/": TOKEN_CODES["DIVIDE"],
        "%": TOKEN_CODES["MODULE"],
        "(": TOKEN_CODES["OPEN_PAREN"],
        ")": TOKEN_CODES["CLOSE_PAREN"],
    }

    def __init__(self, lang):
        self.lang = lang
        self.TOKEN_TYPES = {
            code: self.lang.translate(label_key)
            for code, label_key in self.TOKEN_LABEL_KEYS.items()
        }

    def analyze(self, text):
        self.text = text
        self.tokens = []
        self.errors = []
        self.position = 0
        self.line = 1
        self.column = 1

        while self.position < len(self.text):
            current_char = self.text[self.position]

            if current_char in (" ", "\t"):
                self._process_space()
            elif current_char in self.SINGLE_CHAR_TOKENS:
                self._add_token(self.SINGLE_CHAR_TOKENS[current_char], current_char)
                self._advance()
            elif current_char.isalpha() or current_char == "_":
                self._process_identifier()
            elif current_char.isdigit():
                self._process_number()
            elif current_char in ("\n", "\r"):
                self._advance()
            else:
                self._process_invalid_fragment()

        return self.tokens, self.errors

    def _advance(self):
        if self.position >= len(self.text):
            return

        if self.text[self.position] == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        self.position += 1

    def _process_space(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position

        while self.position < len(self.text) and self.text[self.position] in (" ", "\t"):
            self._advance()

        lexeme = self.text[start_pos:self.position]
        self.tokens.append(
            {
                "code": self.TOKEN_CODES["SPACE"],
                "type": self.TOKEN_TYPES[self.TOKEN_CODES["SPACE"]],
                "lexeme": lexeme,
                "location": self._format_location(start_line, start_col, self.column - 1),
            }
        )

    def _process_identifier(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position

        while self.position < len(self.text):
            current_char = self.text[self.position]
            if not (current_char.isalnum() or current_char == "_"):
                break
            self._advance()

        lexeme = self.text[start_pos:self.position]
        self.tokens.append(
            {
                "code": self.TOKEN_CODES["IDENTIFIER"],
                "type": self.TOKEN_TYPES[self.TOKEN_CODES["IDENTIFIER"]],
                "lexeme": lexeme,
                "location": self._format_location(start_line, start_col, self.column - 1),
            }
        )

    def _process_number(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position
        has_fraction = False

        while self.position < len(self.text) and self.text[self.position].isdigit():
            self._advance()

        if self.position < len(self.text) and self.text[self.position] == ".":
            has_fraction = True
            self._advance()
            while self.position < len(self.text) and self.text[self.position].isdigit():
                self._advance()

        lexeme = self.text[start_pos:self.position]
        token_code = self.TOKEN_CODES["FLOAT"] if has_fraction else self.TOKEN_CODES["INTEGER"]
        self.tokens.append(
            {
                "code": token_code,
                "type": self.TOKEN_TYPES[token_code],
                "lexeme": lexeme,
                "location": self._format_location(start_line, start_col, self.column - 1),
            }
        )

    def _process_invalid_fragment(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position

        while self.position < len(self.text):
            current_char = self.text[self.position]
            if (
                current_char in self.SINGLE_CHAR_TOKENS
                or current_char in (" ", "\t", "\n", "\r")
                or current_char.isalnum()
                or current_char == "_"
            ):
                break
            self._advance()

        if start_pos == self.position:
            self._advance()

        lexeme = self.text[start_pos:self.position]
        self.errors.append(
            {
                "code": "Error",
                "type": self.lang.translate("invalid_char"),
                "analysis_type": "lexical",
                "lexeme": lexeme,
                "location": self._format_location(start_line, start_col, self.column - 1),
            }
        )

    def _add_token(self, code, lexeme):
        start_col = self.column
        end_col = start_col + len(lexeme) - 1
        self.tokens.append(
            {
                "code": code,
                "type": self.TOKEN_TYPES[code],
                "lexeme": lexeme,
                "location": self._format_location(self.line, start_col, end_col),
            }
        )

    def _format_location(self, line, start_col, end_col):
        return f"{self.lang.translate('line_num').format(line)}, {start_col}-{end_col}"
