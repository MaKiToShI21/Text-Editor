from lexer import LexicalAnalyzer


class Parser:
    """
    DFA-based parser for:
    std::complex<double> my_complex(-10.0, 2.0);

    Error neutralization uses Irons-style recovery:
    1) insertion of a missing expected symbol,
    2) substitution of a wrong current symbol,
    3) deletion of extra symbols until synchronization.
    """

    INVALID_LEXEME_CODE = 0

    # Linear DFA states: 0 -> 13 (accepting)
    # NUMBER is a synthetic symbol: optional '-' + FLOAT token.
    STATE_EXPECTED = [
        "KEYWORD_STD",
        "DOUBLE_COLON",
        "KEYWORD_COMPLEX",
        "OPEN_ANGLE",
        "KEYWORD_DOUBLE",
        "CLOSE_ANGLE",
        "IDENTIFIER",
        "OPEN_PAREN",
        "NUMBER",
        "COMMA",
        "NUMBER",
        "CLOSE_PAREN",
        "SEMICOLON",
    ]

    # Per-state synchronization symbols (Irons anchors).
    # These are the nearest symbols we can safely continue from.
    STATE_SYNC = [
        {"DOUBLE_COLON"},           # after std
        {"KEYWORD_COMPLEX"},        # after ::
        {"OPEN_ANGLE"},             # after complex
        {"KEYWORD_DOUBLE"},         # after <
        {"CLOSE_ANGLE"},            # after double
        {"IDENTIFIER"},             # after >
        {"OPEN_PAREN"},             # after identifier
        {"MINUS", "FLOAT"},         # after (
        {"COMMA"},                  # after first number
        {"MINUS", "FLOAT"},         # after comma
        {"CLOSE_PAREN"},            # after second number
        {"SEMICOLON"},              # after )
        set(),                      # after ;
    ]

    def __init__(self, lang):
        self.lang = lang
        self.errors = []
        self.tokens = []
        self.token_types = {}
        self.pos = 0
        self.state = 0

    def parse(self, text):
        lexer = LexicalAnalyzer(self.lang)
        raw_tokens, lex_errors = lexer.analyze(text)

        # Keep lexical errors and continue syntax analysis on valid tokens.
        self.errors = list(lex_errors)
        self.tokens = [t for t in raw_tokens if t["code"] != LexicalAnalyzer.TOKEN_CODES["SPACE"]]
        self.token_types = lexer.TOKEN_TYPES
        self.pos = 0
        self.state = 0

        while self.state < len(self.STATE_EXPECTED):
            expected_symbol = self.STATE_EXPECTED[self.state]
            if not self._consume_expected_with_recovery(expected_symbol):
                break
            self.state += 1

        if self.state == len(self.STATE_EXPECTED) and self._current() is not None:
            token = self._current()
            self.errors.append(
                {
                    "code": "ERROR",
                    "type": self.lang.translate("invalid_char"),
                    "lexeme": token.get("lexeme", ""),
                    "location": token.get("location", "EOF"),
                }
            )

        return self.tokens, self.errors

    def _consume_expected_with_recovery(self, expected_symbol):
        # Normal consume
        if self._match_symbol_at_current(expected_symbol):
            self._consume_symbol(expected_symbol)
            return True

        token = self._current()
        self._add_expected_error(expected_symbol, token)

        # EOF: cannot recover further
        if token is None:
            return False

        # Irons #1 (insertion): current token is a known synchronization anchor.
        if self._token_is_state_sync(token):
            return True

        # Irons #2 (substitution): next token can satisfy current expected symbol.
        next_token = self._peek()
        if next_token is not None and self._token_matches_symbol(next_token, expected_symbol):
            self.pos += 1
            return self._consume_expected_if_matches(expected_symbol)

        # Irons #3 (deletion): drop tokens until expected or future sync.
        while self._current() is not None:
            if self._match_symbol_at_current(expected_symbol):
                self._consume_symbol(expected_symbol)
                return True
            if self._token_is_state_sync(self._current()):
                return True
            self.pos += 1

        return False

    def _consume_expected_if_matches(self, expected_symbol):
        if self._match_symbol_at_current(expected_symbol):
            self._consume_symbol(expected_symbol)
            return True
        return False

    def _match_symbol_at_current(self, symbol):
        token = self._current()
        return token is not None and self._token_matches_symbol(token, symbol)

    def _consume_symbol(self, symbol):
        if symbol == "NUMBER":
            if self._current() is not None and self._current()["code"] == LexicalAnalyzer.TOKEN_CODES["MINUS"]:
                self.pos += 1
            float_token = self._current()
            if float_token is not None:
                self._validate_float_lexeme(float_token)
            self.pos += 1
            return
        self.pos += 1

    def _token_is_state_sync(self, token):
        for symbol in self.STATE_SYNC[self.state]:
            if self._token_matches_symbol(token, symbol):
                return True
        return False

    def _token_matches_symbol(self, token, symbol):
        codes = LexicalAnalyzer.TOKEN_CODES
        code = token["code"]

        if symbol == "NUMBER":
            if code == codes["MINUS"]:
                nxt = self._peek()
                return nxt is not None and self._is_valid_float_token(nxt)
            return self._is_valid_float_token(token)

        expected_code = codes[symbol]
        if code != expected_code:
            return False

        if symbol == "IDENTIFIER":
            return self._is_valid_identifier(token.get("lexeme", ""))
        if symbol == "KEYWORD_STD":
            return token.get("lexeme", "") == "std"
        if symbol == "KEYWORD_COMPLEX":
            return token.get("lexeme", "") == "complex"
        if symbol == "KEYWORD_DOUBLE":
            return token.get("lexeme", "") == "double"
        return True

    def _is_valid_identifier(self, lexeme):
        if not lexeme:
            return False
        first = lexeme[0]
        if not (first == "_" or self._is_letter(first)):
            return False
        for ch in lexeme[1:]:
            if not (self._is_letter(ch) or self._is_digit(ch) or ch == "_"):
                return False
        return True

    def _is_valid_float_token(self, token):
        if token["code"] != LexicalAnalyzer.TOKEN_CODES["FLOAT"]:
            return False
        lexeme = token.get("lexeme", "")
        parts = lexeme.split(".")
        if len(parts) != 2:
            return False
        left, right = parts
        return bool(left) and bool(right) and left.isdigit() and right.isdigit()

    def _validate_float_lexeme(self, token):
        if not self._is_valid_float_token(token):
            self.errors.append(
                {
                    "code": "ERROR",
                    "type": "Expected floating-point number",
                    "lexeme": token.get("lexeme", ""),
                    "location": token.get("location", "EOF"),
                }
            )

    def _add_expected_error(self, expected_symbol, token):
        if expected_symbol == "NUMBER":
            expected_name = self.lang.translate("float")
        else:
            expected_name = self.token_types.get(
                LexicalAnalyzer.TOKEN_CODES[expected_symbol],
                expected_symbol,
            )

        self.errors.append(
            {
                "code": "ERROR",
                "type": f"Ожидалось: {expected_name}",
                "lexeme": "" if token is None else token.get("lexeme", ""),
                "location": "EOF" if token is None else token.get("location", "EOF"),
            }
        )

    def _current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _peek(self):
        idx = self.pos + 1
        if idx < len(self.tokens):
            return self.tokens[idx]
        return None

    @staticmethod
    def _is_letter(ch):
        return ("a" <= ch <= "z") or ("A" <= ch <= "Z")

    @staticmethod
    def _is_digit(ch):
        return "0" <= ch <= "9"
