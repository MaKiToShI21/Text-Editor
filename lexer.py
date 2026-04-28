class LexicalAnalyzer:
    def __init__(self, lang='ru'):
        self.lang = lang

        self.TOKEN_TYPES = {
            1: self.lang.translate('kw_double'),
            2: self.lang.translate('kw_std'),
            3: self.lang.translate('kw_complex'),
            4: self.lang.translate('identifier'),
            5: self.lang.translate('space'),
            6: self.lang.translate('integer'),
            7: self.lang.translate('float'),
            8: self.lang.translate('double_colon'),
            9: self.lang.translate('open_angle'),
            10: self.lang.translate('close_angle'),
            11: self.lang.translate('open_paren'),
            12: self.lang.translate('close_paren'),
            13: self.lang.translate('minus'),
            14: self.lang.translate('comma'),
            15: self.lang.translate('semicolon')
        }

    TOKEN_CODES = {
        'KEYWORD_DOUBLE': 1,
        'KEYWORD_STD': 2,
        'KEYWORD_COMPLEX': 3,
        'IDENTIFIER': 4,
        'SPACE': 5,
        'INTEGER': 6,
        'FLOAT': 7,
        'DOUBLE_COLON': 8,
        'OPEN_ANGLE': 9,
        'CLOSE_ANGLE': 10,
        'OPEN_PAREN': 11,
        'CLOSE_PAREN': 12,
        'MINUS': 13,
        'COMMA': 14,
        'SEMICOLON': 15,
    }

    KEYWORDS = {
        'double': TOKEN_CODES['KEYWORD_DOUBLE'],
        'std': TOKEN_CODES['KEYWORD_STD'],
        'complex': TOKEN_CODES['KEYWORD_COMPLEX']
    }

    def analyze(self, text):
        self.text = text
        self._lines = text.splitlines() or [text]
        self.tokens = []
        self.errors = []
        self.position = 0
        self.line = 1
        self.column = 1

        while self.position < len(self.text):
            current_char = self.text[self.position]

            if current_char == ' ':
                self._process_space()
            elif current_char.isalpha() or current_char == '_':
                self._process_identifier_or_keyword()
            elif current_char.isdigit():
                self._process_number()
            elif current_char == ':':
                self._process_double_colon()
            elif current_char == '<':
                self._add_token(self.TOKEN_CODES['OPEN_ANGLE'], '<')
                self._advance()
            elif current_char == '>':
                self._add_token(self.TOKEN_CODES['CLOSE_ANGLE'], '>')
                self._advance()
            elif current_char == '(':
                self._add_token(self.TOKEN_CODES['OPEN_PAREN'], '(')
                self._advance()
            elif current_char == ')':
                self._add_token(self.TOKEN_CODES['CLOSE_PAREN'], ')')
                self._advance()
            elif current_char == '-':
                self._add_token(self.TOKEN_CODES['MINUS'], '-')
                self._advance()
            elif current_char == ',':
                self._add_token(self.TOKEN_CODES['COMMA'], ',')
                self._advance()
            elif current_char == ';':
                self._add_token(self.TOKEN_CODES['SEMICOLON'], ';')
                self._advance()
            elif current_char.isspace():
                self._advance()
            else:
                self._add_error(current_char)
                self._advance()

        return self.tokens, self.errors

    def _advance(self):
        if self.position < len(self.text):
            if self.text[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

    def _add_token(self, code, lexeme):
        start_col = self.column
        end_col = start_col + len(lexeme) - 1
        self.tokens.append({
            'code': code,
            'type': self.TOKEN_TYPES[code],
            'lexeme': lexeme,
            'location': f"{self.lang.translate('line_num').format(self.line, 0)}, {start_col}-{end_col}",
        })

    def _add_error(self, lexeme):
        start_col = self.column
        end_col = start_col + len(lexeme) - 1

        if self.errors:
            last = self.errors[-1]
            last_line = last.get('line')
            last_end = last.get('end_col')
            if last_line == self.line and isinstance(last_end, int) and start_col > last_end:
                between_text = ''
                line_text = self._lines[self.line - 1] if 1 <= self.line <= len(self._lines) else ''

                if start_col > last_end + 1:
                    between_text = line_text[last_end:start_col - 1]

                if start_col == last_end + 1 or (between_text and all(ch == ' ' for ch in between_text)):
                    last['lexeme'] += between_text + lexeme
                    last['end_col'] = end_col
                    last['location'] = (
                        f"{self.lang.translate('line_num').format(self.line, 0)}, "
                        f"{last['start_col']}-{last['end_col']}"
                    )
                    return

        self.errors.append({
            'code': 'ERROR',
            'type': self.lang.translate('invalid_char'),
            'lexeme': lexeme,
            'location': f"{self.lang.translate('line_num').format(self.line, 0)}, {start_col}-{end_col}",
            'line': self.line,
            'start_col': start_col,
            'end_col': end_col,
        })

    def _process_identifier_or_keyword(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position

        while (self.position < len(self.text) and
               (self.text[self.position].isalnum() or self.text[self.position] == '_')):
            self._advance()

        lexeme = self.text[start_pos:self.position]
        code = self.KEYWORDS.get(lexeme, self.TOKEN_CODES['IDENTIFIER'])

        self.tokens.append({
            'code': code,
            'type': self.TOKEN_TYPES[code],
            'lexeme': lexeme,
            'location': f"{self.lang.translate('line_num').format(start_line, 0)}, {start_col}-{self.column - 1}",
        })

    def _process_space(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position

        while (self.position < len(self.text) and
               self.text[self.position] == ' '):
            self._advance()

        lexeme = self.text[start_pos:self.position]
        end_col = self.column - 1

        self.tokens.append({
            'code': self.TOKEN_CODES['SPACE'],
            'type': self.TOKEN_TYPES[self.TOKEN_CODES['SPACE']],
            'lexeme': lexeme,
            'location': f"{self.lang.translate('line_num').format(start_line, 0)}, {start_col}-{end_col}",
        })

    def _process_number(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position
        has_fraction = False

        while (self.position < len(self.text) and
               self.text[self.position].isdigit()):
            self._advance()

        if (self.position < len(self.text) and
            self.text[self.position] == '.'):
            has_fraction = True
            self._advance()

            while (self.position < len(self.text) and
                   self.text[self.position].isdigit()):
                self._advance()

        lexeme = self.text[start_pos:self.position]
        code = self.TOKEN_CODES['FLOAT'] if has_fraction else self.TOKEN_CODES['INTEGER']

        self.tokens.append({
            'code': code,
            'type': self.TOKEN_TYPES[code],
            'lexeme': lexeme,
            'location': f"{self.lang.translate('line_num').format(start_line, 0)}, {start_col}-{self.column - 1}",
        })

    def _process_double_colon(self):
        start_line = self.line
        start_col = self.column

        has_double_colon = (
            self.position + 1 < len(self.text) and
            self.text[self.position + 1] == ':'
        )

        if has_double_colon:
            self._advance()
            self._advance()
            self.tokens.append({
                'code': self.TOKEN_CODES['DOUBLE_COLON'],
                'type': self.TOKEN_TYPES[self.TOKEN_CODES['DOUBLE_COLON']],
                'lexeme': '::',
                'location': f"{self.lang.translate('line_num').format(start_line, 0)}, {start_col}-{self.column - 1}",
            })

        should_add_colon_error = (
            not has_double_colon or
            (self.position < len(self.text) and self.text[self.position] == ':')
        )

        if should_add_colon_error:
            self._add_error(':')
            self._advance()
