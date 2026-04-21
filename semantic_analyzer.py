from decimal import Decimal, InvalidOperation
import re

from lexer import LexicalAnalyzer


class SemanticAnalyzer:
    DOUBLE_MAX = Decimal("1.7976931348623157e308")
    DOUBLE_MIN_SUBNORMAL = Decimal("4.9406564584124654e-324")

    def __init__(self, lang):
        self.lang = lang
        self.errors = []
        self.symbol_table = {}

    def analyze(self, text):
        lexer = LexicalAnalyzer(self.lang)
        tokens, _ = lexer.analyze(text)
        self.errors = []
        self.symbol_table = {}

        lines = self._split_tokens_by_line(tokens)
        for _, line_tokens in lines:
            self._analyze_line(line_tokens)

        return self.errors

    def _analyze_line(self, line_tokens):
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        identifier_code = LexicalAnalyzer.TOKEN_CODES["IDENTIFIER"]
        open_paren_code = LexicalAnalyzer.TOKEN_CODES["OPEN_PAREN"]
        close_paren_code = LexicalAnalyzer.TOKEN_CODES["CLOSE_PAREN"]
        minus_code = LexicalAnalyzer.TOKEN_CODES["MINUS"]
        integer_code = LexicalAnalyzer.TOKEN_CODES["INTEGER"]
        float_code = LexicalAnalyzer.TOKEN_CODES["FLOAT"]

        significant = [t for t in line_tokens if t["code"] != space_code]
        if not significant:
            return

        identifier_token = None
        open_paren_idx = None
        for idx, token in enumerate(significant):
            if token["code"] == open_paren_code:
                open_paren_idx = idx
                break

        if open_paren_idx is not None:
            for token in significant[:open_paren_idx]:
                if token["code"] == identifier_code:
                    identifier_token = token
                    break

        if identifier_token is None:
            return

        self._check_identifier_uniqueness(identifier_token)

        close_paren_idx = None
        for idx in range(open_paren_idx + 1, len(significant)):
            if significant[idx]["code"] == close_paren_code:
                close_paren_idx = idx
                break

        if close_paren_idx is None:
            return

        prev_non_space = None
        for idx in range(open_paren_idx + 1, close_paren_idx):
            token = significant[idx]
            code = token["code"]

            if code not in (integer_code, float_code):
                prev_non_space = token
                continue

            has_minus = prev_non_space is not None and prev_non_space["code"] == minus_code

            if code == integer_code:
                self.errors.append(
                    {
                        "message": self.lang.translate("semantic_type_mismatch").format(token["lexeme"]),
                        "location": token["location"],
                    }
                )

            if not self._is_double_value_in_range(token["lexeme"], has_minus):
                preview = self._build_short_value_preview(token["lexeme"], has_minus)
                self.errors.append(
                    {
                        "message": self.lang.translate("semantic_out_of_range").format(preview),
                        "location": token["location"],
                    }
                )

            prev_non_space = token

    def _check_identifier_uniqueness(self, identifier_token):
        identifier = identifier_token["lexeme"]
        existing = self.symbol_table.get(identifier)

        if existing is not None:
            first_line, _, _ = self._extract_location(existing["location"])
            self.errors.append(
                {
                    "message": self.lang.translate("semantic_duplicate_identifier").format(
                        identifier,
                        first_line if first_line is not None else "?",
                    ),
                    "location": identifier_token["location"],
                }
            )
            return

        self.symbol_table[identifier] = identifier_token

    def _is_double_value_in_range(self, lexeme, is_negative):
        number_text = f"-{lexeme}" if is_negative else lexeme
        try:
            value = Decimal(number_text)
        except InvalidOperation:
            return False

        abs_value = abs(value)
        if abs_value == 0:
            return True
        if abs_value > self.DOUBLE_MAX:
            return False
        if abs_value < self.DOUBLE_MIN_SUBNORMAL:
            return False
        return True

    @staticmethod
    def _build_short_value_preview(lexeme, is_negative):
        full_value = f"-{lexeme}" if is_negative else lexeme
        if len(full_value) <= 5:
            return full_value
        return f"{full_value[:5]}..."

    def _split_tokens_by_line(self, tokens):
        lines = {}
        for token in tokens:
            line, _, _ = self._extract_location(token.get("location", ""))
            if line is None:
                continue
            lines.setdefault(line, []).append(token)

        return sorted(lines.items(), key=lambda item: item[0])

    @staticmethod
    def _extract_location(location):
        numbers = re.findall(r"\d+", location or "")
        if len(numbers) < 3:
            return None, None, None
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
