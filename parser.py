from dataclasses import dataclass, field

from lexer import LexicalAnalyzer


@dataclass
class ExpressionValue:
    text: str
    postfix: list[str] = field(default_factory=list)
    is_integer_only: bool = False
    value: int | None = None
    evaluation_error: str | None = None


@dataclass
class LineAnalysis:
    line_no: int
    expression: str
    location: str
    quadruples: list[tuple[str, str, str, str]] = field(default_factory=list)
    postfix: list[str] | None = None
    value: str = ""
    integer_only: bool = False


@dataclass
class ParseSession:
    tokens: list[dict]
    errors: list[dict]
    line_results: list[LineAnalysis]


class Parser:
    """Recursive-descent parser for: E→TA, A→ε|+TA|-TA, T→FB, B→ε|*FB|/FB|%FB, F→num|id|(E)."""

    def __init__(self, lang):
        self.lang = lang
        self.tokens = []
        self.errors = []
        self.line_results = []
        self._current_tokens = []
        self._position = 0
        self._temp_index = 0
        self._quadruples = []

    def parse(self, text):
        session = self.analyze(text, collect_ir=False)
        return session.tokens, session.errors

    def analyze(self, text, collect_ir=False):
        lexer = LexicalAnalyzer(self.lang)
        tokens, lexical_errors = lexer.analyze(text)

        self.tokens = tokens
        self.errors = []
        self.line_results = []

        tokens_by_line = self._group_tokens_by_line(tokens)
        lexical_by_line = self._group_entries_by_line(lexical_errors)

        line_count = max(
            len(text.splitlines()),
            max(tokens_by_line.keys(), default=0),
            max(lexical_by_line.keys(), default=0),
        )

        for line_no in range(1, line_count + 1):
            line_tokens = tokens_by_line.get(line_no, [])
            significant = self._significant_tokens(line_tokens)
            if not significant and line_no not in lexical_by_line:
                continue

            line_errors = lexical_by_line.get(line_no, [])
            if line_errors:
                for error in line_errors:
                    self.errors.append(
                        {
                            "analysis_type": "lexical",
                            "lexeme": error.get("lexeme", ""),
                            "description": error.get("type", self.lang.translate("invalid_char")),
                            "location": error.get("location", ""),
                        }
                    )
                continue

            line_result = self._parse_line(line_no, significant, collect_ir)
            if line_result is not None:
                self.line_results.append(line_result)

        return ParseSession(self.tokens, self.errors, self.line_results)

    def _parse_line(self, line_no, tokens, collect_ir):
        self._current_tokens = tokens
        self._position = 0
        self._temp_index = 0
        self._quadruples = []

        expression = "".join(token["lexeme"] for token in tokens)
        first_location = tokens[0].get("location", "")

        value = self._parse_E()
        if value is None:
            return None

        if self._position < len(self._current_tokens):
            token = self._current_tokens[self._position]
            if self._is_operand_start(token):
                self._add_syntax_error(
                    token,
                    self.lang.translate("parser_expected_operator"),
                )
            elif token["code"] == LexicalAnalyzer.TOKEN_CODES["CLOSE_PAREN"]:
                self._add_syntax_error(
                    token,
                    self.lang.translate("parser_unexpected_closing_paren"),
                )
            else:
                self._add_syntax_error(
                    token,
                    self.lang.translate("parser_unexpected_token").format(token["lexeme"]),
                )
            return None

        if value.evaluation_error:
            self._add_semantic_error(
                expression,
                value.evaluation_error,
                first_location,
            )

        result = LineAnalysis(
            line_no=line_no,
            expression=expression,
            location=first_location,
            quadruples=list(self._quadruples) if collect_ir else [],
            postfix=value.postfix if collect_ir and value.is_integer_only else None,
            value=self._format_value(value) if collect_ir else "",
            integer_only=value.is_integer_only,
        )
        return result

    def _parse_E(self):
        """E → TA"""
        first = self._parse_T()
        if first is None:
            return None
        return self._parse_A(first)

    def _parse_A(self, left):
        """A → ε | +TA | -TA (left-associative loop)."""
        codes = LexicalAnalyzer.TOKEN_CODES
        while True:
            tok = self._current_token()
            if tok is None:
                break
            if tok["code"] not in (codes["PLUS"], codes["MINUS"]):
                break
            self._position += 1
            right = self._parse_T()
            if right is None:
                return None
            left = self._combine_binary(left, tok, right)
        return left

    def _parse_T(self):
        """T → FB"""
        first = self._parse_F()
        if first is None:
            return None
        return self._parse_B(first)

    def _parse_B(self, left):
        """B → ε | *FB | /FB | %FB"""
        codes = LexicalAnalyzer.TOKEN_CODES
        while True:
            tok = self._current_token()
            if tok is None:
                break
            if tok["code"] not in (codes["MULTIPLY"], codes["DIVIDE"], codes["MODULE"]):
                break
            self._position += 1
            right = self._parse_F()
            if right is None:
                return None
            left = self._combine_binary(left, tok, right)
        return left

    def _parse_F(self):
        """F → num | id | (E); unary +/- handled as extension before factor."""
        token = self._current_token()
        if token is None:
            self._add_eof_error(self.lang.translate("parser_expected_operand"))
            return None

        token_code = token["code"]
        codes = LexicalAnalyzer.TOKEN_CODES

        if token_code == codes["PLUS"]:
            self._position += 1
            return self._parse_F()

        if token_code == codes["MINUS"]:
            self._position += 1
            operand = self._parse_F()
            if operand is None:
                return None
            return self._apply_unary_minus(operand)

        if token_code in (codes["INTEGER"], codes["FLOAT"], codes["IDENTIFIER"]):
            self._position += 1
            return self._build_atom(token)

        if token_code == codes["OPEN_PAREN"]:
            self._position += 1
            nested = self._parse_E()
            if nested is None:
                return None

            if not self._match_code("CLOSE_PAREN"):
                self._add_missing_closing_paren_error()
                return None
            return nested

        if token_code == codes["CLOSE_PAREN"]:
            self._add_syntax_error(token, self.lang.translate("parser_unexpected_closing_paren"))
            return None

        self._add_syntax_error(token, self.lang.translate("parser_expected_operand"))
        return None

    def _build_atom(self, token):
        token_code = token["code"]
        if token_code == LexicalAnalyzer.TOKEN_CODES["INTEGER"]:
            return ExpressionValue(
                text=token["lexeme"],
                postfix=[token["lexeme"]],
                is_integer_only=True,
                value=int(token["lexeme"]),
            )

        if token_code == LexicalAnalyzer.TOKEN_CODES["FLOAT"]:
            return ExpressionValue(
                text=token["lexeme"],
                postfix=[token["lexeme"]],
                is_integer_only=False,
                value=None,
            )

        return ExpressionValue(
            text=token["lexeme"],
            postfix=[token["lexeme"]],
            is_integer_only=False,
            value=None,
        )

    def _apply_unary_minus(self, operand):
        result_text = self._new_temp()
        self._quadruples.append(("uminus", operand.text, "-", result_text))

        value = None
        evaluation_error = operand.evaluation_error
        if operand.is_integer_only and operand.value is not None and evaluation_error is None:
            value = -operand.value

        return ExpressionValue(
            text=result_text,
            postfix=operand.postfix + ["NEG"],
            is_integer_only=operand.is_integer_only,
            value=value,
            evaluation_error=evaluation_error,
        )

    def _combine_binary(self, left, operator_token, right):
        operator_lexeme = operator_token["lexeme"]
        result_text = self._new_temp()
        self._quadruples.append((operator_lexeme, left.text, right.text, result_text))

        integer_only = left.is_integer_only and right.is_integer_only
        evaluation_error = left.evaluation_error or right.evaluation_error
        value = None

        if integer_only and evaluation_error is None and left.value is not None and right.value is not None:
            if operator_lexeme == "+":
                value = left.value + right.value
            elif operator_lexeme == "-":
                value = left.value - right.value
            elif operator_lexeme == "*":
                value = left.value * right.value
            elif operator_lexeme == "/":
                if right.value == 0:
                    evaluation_error = self.lang.translate("division_by_zero")
                else:
                    value = left.value // right.value
            elif operator_lexeme == "%":
                if right.value == 0:
                    evaluation_error = self.lang.translate("module_by_zero")
                else:
                    value = left.value % right.value

        return ExpressionValue(
            text=result_text,
            postfix=left.postfix + right.postfix + [operator_lexeme],
            is_integer_only=integer_only,
            value=value,
            evaluation_error=evaluation_error,
        )

    def _format_value(self, value):
        if not value.is_integer_only:
            return self.lang.translate("value_not_available")
        if value.evaluation_error:
            return value.evaluation_error
        if value.value is None:
            return self.lang.translate("value_not_available")
        return str(value.value)

    def _new_temp(self):
        self._temp_index += 1
        return f"t{self._temp_index}"

    def _current_token(self):
        if self._position >= len(self._current_tokens):
            return None
        return self._current_tokens[self._position]

    def _match_code(self, *names):
        token = self._current_token()
        if token is None:
            return False

        valid_codes = {LexicalAnalyzer.TOKEN_CODES[name] for name in names}
        if token["code"] not in valid_codes:
            return False

        self._position += 1
        return True

    def _add_syntax_error(self, token, description):
        self.errors.append(
            {
                "analysis_type": "syntax",
                "lexeme": token.get("lexeme", ""),
                "description": description,
                "location": token.get("location", ""),
            }
        )

    def _add_semantic_error(self, lexeme, description, location):
        self.errors.append(
            {
                "analysis_type": "semantic",
                "lexeme": lexeme,
                "description": description,
                "location": location,
            }
        )

    def _add_eof_error(self, description):
        location = ""
        if self._current_tokens:
            location = self._current_tokens[-1].get("location", "")
        self.errors.append(
            {
                "analysis_type": "syntax",
                "lexeme": "EOF",
                "description": description,
                "location": location,
            }
        )

    def _add_missing_closing_paren_error(self):
        if self._position < len(self._current_tokens):
            token = self._current_tokens[self._position]
            self._add_syntax_error(token, self.lang.translate("parser_expected_closing_paren"))
            return

        self._add_eof_error(self.lang.translate("parser_expected_closing_paren"))

    @staticmethod
    def _group_tokens_by_line(tokens):
        grouped = {}
        for token in tokens:
            line_no = Parser._extract_line_number(token.get("location", ""))
            if line_no is None:
                continue
            grouped.setdefault(line_no, []).append(token)
        return grouped

    @staticmethod
    def _group_entries_by_line(entries):
        grouped = {}
        for entry in entries:
            line_no = Parser._extract_line_number(entry.get("location", ""))
            if line_no is None:
                continue
            grouped.setdefault(line_no, []).append(entry)
        return grouped

    @staticmethod
    def _extract_line_number(location):
        digits = []
        current = ""
        for char in location:
            if char.isdigit():
                current += char
            elif current:
                digits.append(current)
                break
        if current and not digits:
            digits.append(current)
        if not digits:
            return None
        return int(digits[0])

    @staticmethod
    def _significant_tokens(tokens):
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        return [token for token in tokens if token.get("code") != space_code]

    @staticmethod
    def _is_operand_start(token):
        return token["code"] in {
            LexicalAnalyzer.TOKEN_CODES["IDENTIFIER"],
            LexicalAnalyzer.TOKEN_CODES["INTEGER"],
            LexicalAnalyzer.TOKEN_CODES["FLOAT"],
            LexicalAnalyzer.TOKEN_CODES["OPEN_PAREN"],
        }
