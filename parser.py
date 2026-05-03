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
    quadruples: list[tuple[str, str, str, str]] = field(default_factory=list)
    postfix: list[str] | None = None
    value: str = ""


@dataclass
class ParseSession:
    tokens: list[dict]
    errors: list[dict]
    line_results: list[LineAnalysis]


class Parser:
    """Recursive-descent parser with error neutralization.

    Grammar: E→TA, A→ε|+TA|-TA, T→FB, B→ε|*FB|/FB|%FB, F→num|id|(E)

    Error neutralization rules:
      - Parsing does not stop at the first error; it continues through the input.
      - Consecutive errors (at adjacent token positions) are suppressed:
        only the very first of a consecutive run is reported.
      - Non-consecutive errors (separated by at least one successfully consumed
        token) are each reported independently.
    """

    def __init__(self, lang):
        self.lang = lang
        self.tokens = []
        self.errors = []
        self.line_results = []
        self._current_tokens = []
        self._position = 0
        self._temp_index = 0
        self._quadruples = []
        self._last_error_pos = None  # token index of the last reported/suppressed error

    # ------------------------------------------------------------------ public

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

    def format_ir_report(self, session: ParseSession) -> str:
        """Format the intermediate representation (quadruples + RPN) report."""
        lines: list[str] = []

        if session.errors:
            lines.append(self.lang.translate("ir_skipped_due_to_errors"))
            lines.append("")

        if not session.line_results:
            if not session.errors:
                lines.append(self.lang.translate("ir_no_expressions"))
            return "\n".join(lines)

        for lr in session.line_results:
            lines.append(f"{self.lang.translate('ir_line')} {lr.line_no}: {lr.expression}")

            lines.append(f"{self.lang.translate('ir_quadruples')}:")
            if lr.quadruples:
                for op, a1, a2, res in lr.quadruples:
                    lines.append(f"  ({op}, {a1}, {a2}, {res})")
            else:
                lines.append(f"  {self.lang.translate('no_quadruples')}")

            lines.append(f"{self.lang.translate('ir_poliz')}:")
            if lr.postfix:
                lines.append(f"  {' '.join(lr.postfix)}")
                if lr.value:
                    lines.append(f"{self.lang.translate('ir_value')}: {lr.value}")
            else:
                lines.append(f"  {self.lang.translate('poliz_not_available')}")

            lines.append("")

        return "\n".join(lines).rstrip()

    # --------------------------------------------------------- line-level parse

    def _parse_line(self, line_no, tokens, collect_ir):
        self._current_tokens = tokens
        self._position = 0
        self._temp_index = 0
        self._quadruples = []
        self._last_error_pos = None

        expression = "".join(token["lexeme"] for token in tokens)

        errors_before = len(self.errors)
        value = self._parse_E()

        # Report errors for any leftover tokens (trailing garbage).
        # Consecutive suppression applies across the leftover loop as well.
        while self._position < len(self._current_tokens):
            token = self._current_tokens[self._position]
            if self._is_operand_start(token):
                self._add_syntax_error(token, self.lang.translate("parser_expected_operator"))
            elif token["code"] == LexicalAnalyzer.TOKEN_CODES["CLOSE_PAREN"]:
                self._add_syntax_error(token, self.lang.translate("parser_unexpected_closing_paren"))
            else:
                self._add_syntax_error(
                    token,
                    self.lang.translate("parser_unexpected_token").format(token["lexeme"]),
                )
            self._position += 1

        # IR is only built for syntactically correct lines.
        if len(self.errors) > errors_before:
            return None

        return LineAnalysis(
            line_no=line_no,
            expression=expression,
            quadruples=list(self._quadruples) if collect_ir else [],
            postfix=value.postfix if collect_ir else None,
            value=self._format_value(value) if collect_ir else "",
        )

    # ---------------------------------------------------- grammar productions

    def _parse_E(self):
        """E → TA"""
        first = self._parse_T()
        return self._parse_A(first)

    def _parse_A(self, left):
        """A → ε | +TA | -TA  (left-associative loop with error recovery)

        When an operand appears where a binary operator is expected, the
        full factor (_parse_F) is consumed so that parenthesised expressions
        like (8 * i) are swallowed as a unit rather than token-by-token.
        """
        codes = LexicalAnalyzer.TOKEN_CODES
        while True:
            tok = self._current_token()
            if tok is None:
                break
            code = tok["code"]
            if code in (codes["PLUS"], codes["MINUS"]):
                self._position += 1
                right = self._parse_T()
                left = self._combine_binary(left, tok, right)
            elif self._is_operand_start(tok):
                self._add_syntax_error(tok, self.lang.translate("parser_expected_operator"))
                self._parse_F()  # consume the full factor (including any sub-expression)
            else:
                break
        return left

    def _parse_T(self):
        """T → FB"""
        first = self._parse_F()
        return self._parse_B(first)

    def _parse_B(self, left):
        """B → ε | *FB | /FB | %FB  (with the same operand-recovery as A)"""
        codes = LexicalAnalyzer.TOKEN_CODES
        while True:
            tok = self._current_token()
            if tok is None:
                break
            code = tok["code"]
            if code in (codes["MULTIPLY"], codes["DIVIDE"], codes["MODULE"]):
                self._position += 1
                right = self._parse_F()
                left = self._combine_binary(left, tok, right)
            elif self._is_operand_start(tok):
                self._add_syntax_error(tok, self.lang.translate("parser_expected_operator"))
                self._parse_F()  # consume the full factor (including any sub-expression)
            else:
                break
        return left

    def _parse_F(self):
        """F → num | id | (E) | unary +/- F

        Error recovery: on an unexpected token, report an error (subject to
        consecutive suppression), skip the token, and retry.  The one
        exception is CLOSE_PAREN: it is reported but NOT consumed, so that
        the enclosing (E) handler can still match it.
        """
        codes = LexicalAnalyzer.TOKEN_CODES
        while True:
            token = self._current_token()
            if token is None:
                self._add_eof_error(self.lang.translate("parser_expected_operand"))
                return self._make_dummy()

            code = token["code"]

            if code == codes["PLUS"]:
                self._position += 1
                return self._parse_F()

            if code == codes["MINUS"]:
                self._position += 1
                operand = self._parse_F()
                return self._apply_unary_minus(operand)

            if code in (codes["INTEGER"], codes["FLOAT"], codes["IDENTIFIER"]):
                self._position += 1
                return self._build_atom(token)

            if code == codes["OPEN_PAREN"]:
                self._position += 1
                nested = self._parse_E()
                if not self._match_code("CLOSE_PAREN"):
                    self._add_missing_closing_paren_error()
                return nested

            if code == codes["CLOSE_PAREN"]:
                # Do NOT consume: leave the ')' for the enclosing (E) handler.
                self._add_syntax_error(token, self.lang.translate("parser_expected_operand"))
                return self._make_dummy()

            # Any other unexpected token: report, skip, retry.
            self._add_syntax_error(token, self.lang.translate("parser_expected_operand"))
            self._position += 1

    # --------------------------------------------------- IR / value builders

    def _make_dummy(self):
        """Placeholder ExpressionValue used during error recovery."""
        t = self._new_temp()
        return ExpressionValue(text=t, postfix=[], is_integer_only=False)

    def _build_atom(self, token):
        codes = LexicalAnalyzer.TOKEN_CODES
        if token["code"] == codes["INTEGER"]:
            return ExpressionValue(
                text=token["lexeme"],
                postfix=[token["lexeme"]],
                is_integer_only=True,
                value=int(token["lexeme"]),
            )
        return ExpressionValue(
            text=token["lexeme"],
            postfix=[token["lexeme"]],
            is_integer_only=False,
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

    def _format_value(self, ev: ExpressionValue) -> str:
        """Return a display string for the computed value (integers only)."""
        if not ev.is_integer_only:
            return ""
        if ev.evaluation_error:
            return ev.evaluation_error
        if ev.value is None:
            return ""
        return str(ev.value)

    def _new_temp(self):
        self._temp_index += 1
        return f"t{self._temp_index}"

    # ----------------------------------------------- token stream primitives

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

    # --------------------------------------------------- error reporting

    def _add_syntax_error(self, token, description, pos=None):
        """Append a syntax error, suppressing it if consecutive with the last."""
        if pos is None:
            pos = self._position
        if self._last_error_pos is not None and pos <= self._last_error_pos + 1:
            self._last_error_pos = pos
            return
        self._last_error_pos = pos
        self.errors.append(
            {
                "analysis_type": "syntax",
                "lexeme": token.get("lexeme", ""),
                "description": description,
                "location": token.get("location", ""),
            }
        )

    def _add_eof_error(self, description):
        """Append an end-of-input error, suppressing it if consecutive."""
        pos = len(self._current_tokens)
        if self._last_error_pos is not None and pos <= self._last_error_pos + 1:
            self._last_error_pos = pos
            return
        self._last_error_pos = pos
        location = self._current_tokens[-1].get("location", "") if self._current_tokens else ""
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
        else:
            self._add_eof_error(self.lang.translate("parser_expected_closing_paren"))

    # ---------------------------------------------------- static helpers

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
