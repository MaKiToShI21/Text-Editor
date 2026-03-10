class LexicalAnalyzer:
    TOKEN_CODES = {
        'KEYWORD_INT': 1,
        'KEYWORD_FLOAT': 2,
        'KEYWORD_DOUBLE': 3,
        'KEYWORD_STD': 4,
        'KEYWORD_COMPLEX': 5,
        'IDENTIFIER': 6,
        'SPACE': 7,
        'INTEGER': 8,
        'FLOAT': 9,
        'DOUBLE_COLON': 10,
        'OPEN_ANGLE': 11,
        'CLOSE_ANGLE': 12,
        'OPEN_PAREN': 13,
        'CLOSE_PAREN': 14,
        'MINUS': 15,
        'COMMA': 16,
        'SEMICOLON': 17
    }

    TOKEN_TYPES = {
        1: 'Ключевое слово int',
        2: 'Ключевое слово float',
        3: 'Ключевое слово double',
        4: 'Ключевое слово std',
        5: 'Ключевое слово complex',
        6: 'Идентификатор',
        7: 'Пробел',
        8: 'Целое число',
        9: 'Число с плавающей точкой',
        10: 'Двойное двоеточие',
        11: 'Открывающая угловая скобка',
        12: 'Закрывающая угловая скобка',
        13: 'Открывающая круглая скобка',
        14: 'Закрывающая круглая скобка',
        15: 'Минус',
        16: 'Запятая',
        17: 'Точка с запятой'
    }

    KEYWORDS = {
        'int': TOKEN_CODES['KEYWORD_INT'],
        'float': TOKEN_CODES['KEYWORD_FLOAT'],
        'double': TOKEN_CODES['KEYWORD_DOUBLE'],
        'std': TOKEN_CODES['KEYWORD_STD'],
        'complex': TOKEN_CODES['KEYWORD_COMPLEX']
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
            'line': self.line,
            'code': code,
            'type': self.TOKEN_TYPES[code],
            'lexeme': lexeme,
            'location': f"{start_col}-{end_col}",
        })

    def _add_error(self, lexeme):
        self.errors.append({
            'line': self.line,
            'code': 'ERROR',
            'type': 'Недопустимый символ',
            'lexeme': lexeme,
            'location': f'{self.column}',
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
            'line': start_line,
            'code': code,
            'type': self.TOKEN_TYPES[code],
            'lexeme': lexeme,
            'location': f"{start_col}-{self.column - 1}",
        })

    def _process_space(self):
        start_line = self.line
        start_col = self.column

        while (self.position < len(self.text) and
               self.text[self.position] == ' '):
            self._advance()

        self.tokens.append({
            'line': start_line,
            'code': self.TOKEN_CODES['SPACE'],
            'type': self.TOKEN_TYPES[self.TOKEN_CODES['SPACE']],
            'lexeme': ' ',
            'location': f"{start_col}-{self.column - 1}",
        })

    def _process_number(self):
        start_line = self.line
        start_col = self.column
        start_pos = self.position
        has_decimal = False

        while (self.position < len(self.text) and
               self.text[self.position].isdigit()):
            self._advance()

        if (self.position < len(self.text) and
            self.text[self.position] == '.'):
            has_decimal = True
            self._advance()

            while (self.position < len(self.text) and
                   self.text[self.position].isdigit()):
                self._advance()

        lexeme = self.text[start_pos:self.position]
        code = self.TOKEN_CODES['FLOAT'] if has_decimal else self.TOKEN_CODES['INTEGER']

        self.tokens.append({
            'line': start_line,
            'code': code,
            'type': self.TOKEN_TYPES[code],
            'lexeme': lexeme,
            'location': f"{start_col}-{self.column - 1}",
        })

    def _process_double_colon(self):
        start_line = self.line
        start_col = self.column

        if (self.position + 1 < len(self.text) and 
            self.text[self.position + 1] == ':'):
            self._advance()
            self._advance()
            self.tokens.append({
                'line': start_line,
                'code': self.TOKEN_CODES['DOUBLE_COLON'],
                'type': self.TOKEN_TYPES[self.TOKEN_CODES['DOUBLE_COLON']],
                'lexeme': '::',
                'location': f"{start_col}-{self.column - 1}",
            })

            if (self.position < len(self.text) and
                self.text[self.position] == ':'):
                self._add_error(':')
                self._advance()
        else:
            self._add_error(':')
            self._advance()


# def main():
#     test_code = 'std:::complex<float> _12complex(-10.0, 2.0);'

#     lexer = LexicalAnalyzer()
#     tokens, errors = lexer.analyze(test_code)

#     print("Исходный код:", test_code)
#     print("\nТокены:")
#     for token in tokens:
#         print(f"  Строка {token['line']}  {token['code']:2}  {token['type']:25}  {repr(token['lexeme']):10}  {token['location']}")

#     if errors:
#         print("\nОшибки:")
#         for error in errors:
#             print(f"  {error['message']} (строка {error['line']}, колонка {error['column']})")


# if __name__ == "__main__":
#     main()
