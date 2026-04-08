from lexer import LexicalAnalyzer


class Parser:
    """
    Recursive-descent parser for the user's CFG from "кс грамматика.docx".

    Error neutralization: Irons-style recovery.
    On mismatch we try, in order:
    1) insertion of a missing expected symbol (keep current token),
    2) substitution of current wrong symbol (consume one token),
    3) deletion of extra symbols until synchronization set.
    """

    CFG = (
        "<Std> -> std <TwoColons>\n"
        "<TwoColons> -> :: <Complex>\n"
        "<Complex> -> complex <TemplateArg> <IdentifierName>\n"
        "<TemplateArg> -> < <Double> >\n"
        "<Double> -> double\n"
        "<IdentifierName> -> <LetterOrUnderscore><IdentifierRem>\n"
        "<LetterOrUnderscore> -> <Letter> | _\n"
        "<IdentifierRem> -> <Letter><IdentifierRem> | <Digit><IdentifierRem> | _<IdentifierRem> | <ParenthesisExpr>\n"
        "<ParenthesisExpr> -> ( <Expression> );\n"
        "<Expression> -> <Number> , <Number>\n"
        "<Number> -> - <Float> | <Float>\n"
        "<Float> -> <Integer> . <Integer>\n"
        "<Integer> -> <Digit><IntegerRem>\n"
        "<IntegerRem> -> <Digit><IntegerRem> | ε\n"
        "<Letter> -> 'a' | ... | 'z' | 'A' | ... | 'Z'\n"
        "<Digit> -> '0' | ... | '9'"
    )

    def __init__(self, lang):
        self.lang = lang
        self.tokens = []
        self.pos = 0
        self.errors = []
        self.token_types = {}

        self.C = LexicalAnalyzer.TOKEN_CODES

    def parse_complex_declaration(self, text):
        lexer = LexicalAnalyzer(self.lang)
        tokens, lex_errors = lexer.analyze(text)

        self.tokens = tokens
        self.pos = 0
        self.errors = list(lex_errors)
        self.token_types = lexer.TOKEN_TYPES

        self._skip_spaces()
        self._parse_std()
        self._skip_spaces()

        if self._current() is not None:
            # Extra tail is one syntax error, not a cascade.
            self._add_error("Extra sequence of symbols", self._current())

    def parse(self, text):
        self.parse_complex_declaration(text)
        return self.errors

    # <Std> -> std <TwoColons>
    def _parse_std(self):
        sync = {
            self.C["DOUBLE_COLON"],
            self.C["KEYWORD_COMPLEX"],
            self.C["OPEN_ANGLE"],
            self.C["KEYWORD_DOUBLE"],
            self.C["IDENTIFIER"],
            self.C["OPEN_PAREN"],
            self.C["FLOAT"],
            self.C["MINUS"],
            self.C["COMMA"],
            self.C["CLOSE_PAREN"],
            self.C["SEMICOLON"],
        }
        if self._expect(self.C["KEYWORD_STD"], "Expected 'std'", sync) is False:
            return
        self._parse_two_colons()

    # <TwoColons> -> :: <Complex>
    def _parse_two_colons(self):
        sync = {
            self.C["KEYWORD_COMPLEX"],
            self.C["OPEN_ANGLE"],
            self.C["KEYWORD_DOUBLE"],
            self.C["IDENTIFIER"],
            self.C["OPEN_PAREN"],
            self.C["FLOAT"],
            self.C["MINUS"],
            self.C["COMMA"],
            self.C["CLOSE_PAREN"],
            self.C["SEMICOLON"],
        }
        if self._expect(self.C["DOUBLE_COLON"], "Expected '::' after 'std'", sync) is False:
            return
        self._parse_complex()

    # <Complex> -> complex <TemplateArg> <IdentifierName>
    def _parse_complex(self):
        sync = {
            self.C["OPEN_ANGLE"],
        }
        if self._expect(self.C["KEYWORD_COMPLEX"], "Expected 'complex'", sync) is False:
            return
        self._parse_template_arg()
        self._parse_identifier_name()

    # <TemplateArg> -> < <Double> >
    def _parse_template_arg(self):
        sync_left = {
            self.C["KEYWORD_DOUBLE"],
            self.C["CLOSE_ANGLE"],
            self.C["IDENTIFIER"],
            self.C["OPEN_PAREN"],
            self.C["SEMICOLON"],
        }
        if self._expect(
            self.C["OPEN_ANGLE"],
            "Expected '<' before template argument",
            sync_left,
        ) is False:
            return

        self._parse_double()

        sync_right = {
            self.C["IDENTIFIER"],
            self.C["OPEN_PAREN"],
            self.C["SEMICOLON"],
        }
        self._expect(
            self.C["CLOSE_ANGLE"],
            "Expected '>' after template argument",
            sync_right,
        )

    # <Double> -> double
    def _parse_double(self):
        sync = {
            self.C["CLOSE_ANGLE"],
            self.C["IDENTIFIER"],
            self.C["OPEN_PAREN"],
            self.C["SEMICOLON"],
        }
        self._expect(
            self.C["KEYWORD_DOUBLE"],
            "Expected 'double' as template argument",
            sync,
        )

    # <IdentifierName> -> <LetterOrUnderscore><IdentifierRem>
    def _parse_identifier_name(self):
        sync = {
            self.C["OPEN_PAREN"],
            self.C["FLOAT"],
            self.C["MINUS"],
            self.C["COMMA"],
            self.C["CLOSE_PAREN"],
            self.C["SEMICOLON"],
        }
        token_result = self._expect(self.C["IDENTIFIER"], "Expected identifier name", sync)
        if token_result is False:
            return
        token = token_result if isinstance(token_result, dict) else None
        if token is None:
            return

        lexeme = token.get("lexeme", "")
        if lexeme:
            if not (self._is_letter(lexeme[0]) or lexeme[0] == "_"):
                self._add_error("Identifier must start with letter or underscore", token)
            for ch in lexeme[1:]:
                if not (self._is_letter(ch) or self._is_digit(ch) or ch == "_"):
                    self._add_error("Identifier contains invalid character", token)
                    break

        self._parse_parenthesis_expr()

    # <ParenthesisExpr> -> ( <Expression> );
    def _parse_parenthesis_expr(self):
        sync_lparen = {
            self.C["FLOAT"],
            self.C["MINUS"],
            self.C["COMMA"],
            self.C["CLOSE_PAREN"],
            self.C["SEMICOLON"],
        }
        if self._expect(
            self.C["OPEN_PAREN"],
            "Expected '(' after identifier",
            sync_lparen,
        ) is False:
            return

        self._parse_expression()

        sync_rparen = {
            self.C["SEMICOLON"],
        }
        if self._expect(
            self.C["CLOSE_PAREN"],
            "Expected ')' after expression",
            sync_rparen,
        ) is False:
            return

        self._expect(
            self.C["SEMICOLON"],
            "Expected ';' after ')'",
            set(),
        )

    # <Expression> -> <Number> , <Number>
    def _parse_expression(self):
        self._parse_number()

        sync_comma = {
            self.C["FLOAT"],
            self.C["MINUS"],
            self.C["CLOSE_PAREN"],
            self.C["SEMICOLON"],
        }
        self._expect(self.C["COMMA"], "Expected ',' between numbers", sync_comma)

        self._parse_number()

    # <Number> -> - <Float> | <Float>
    def _parse_number(self):
        self._skip_spaces()
        if self._match(self.C["MINUS"]):
            self._advance()
            self._skip_spaces()

        sync_float = {
            self.C["COMMA"],
            self.C["CLOSE_PAREN"],
            self.C["SEMICOLON"],
        }
        token_result = self._expect(
            self.C["FLOAT"],
            "Expected floating-point number",
            sync_float,
        )
        if token_result is False:
            return
        token = token_result if isinstance(token_result, dict) else None
        if token is None:
            return
        self._validate_float(token)

    def _validate_float(self, token):
        # Grammar requires <Integer>.<Integer>.
        lexeme = token.get("lexeme", "")
        parts = lexeme.split(".")
        if len(parts) != 2:
            self._add_error("Float must be '<Integer>.<Integer>'", token)
            return
        left, right = parts
        if not left or not right:
            self._add_error("Float must be '<Integer>.<Integer>'", token)
            return
        if not left.isdigit() or not right.isdigit():
            self._add_error("Float must contain digits around '.'", token)

    def _expect(self, expected_code, message, sync_set):
        """
        Irons-style neutralization:
        1) insertion: current token already belongs to sync_set -> assume missing expected token;
        2) substitution: if next token belongs to sync_set -> consume current as wrong token;
        3) deletion: skip symbols until expected/sync token.
        Returns:
        - token dict: exact match consumed;
        - True: recovered (insert/substitute/delete) and can continue;
        - False: EOF/fatal stop.
        """
        self._skip_spaces()
        token = self._current()

        if token is None:
            self._add_error(message, None)
            return False

        if token["code"] == expected_code:
            self._advance()
            return token

        self._add_error(message, token)

        # 1) Insertion: token already good for continuation.
        if token["code"] in sync_set:
            return True

        # 2) Substitution: one wrong token before continuation point.
        next_token = self._peek_next_non_space()
        if next_token is not None and next_token["code"] in sync_set:
            self._advance()
            return True

        # 3) Deletion: remove extra symbols until expected/sync.
        self._advance()
        self._skip_spaces()
        while self._current() is not None:
            code = self._current()["code"]
            if code == expected_code:
                match = self._current()
                self._advance()
                return match
            if code in sync_set:
                return True
            self._advance()
            self._skip_spaces()

        return False

    def _skip_spaces(self):
        while self._current() is not None and self._current()["code"] == self.C["SPACE"]:
            self._advance()

    def _peek_next_non_space(self):
        i = self.pos + 1
        while i < len(self.tokens) and self.tokens[i]["code"] == self.C["SPACE"]:
            i += 1
        if i < len(self.tokens):
            return self.tokens[i]
        return None

    def _match(self, code):
        self._skip_spaces()
        token = self._current()
        return token is not None and token["code"] == code

    def _current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self):
        if self.pos < len(self.tokens):
            self.pos += 1

    def _add_error(self, message, token):
        if token is None:
            location = "EOF"
            lexeme = ""
        else:
            location = token.get("location", "EOF")
            lexeme = token.get("lexeme", "")

        self.errors.append(
            {
                "code": "ERROR",
                "type": message,
                "lexeme": lexeme,
                "location": location,
            }
        )

    @staticmethod
    def _is_letter(ch):
        return ("a" <= ch <= "z") or ("A" <= ch <= "Z")

    @staticmethod
    def _is_digit(ch):
        return "0" <= ch <= "9"
