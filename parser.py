from lexer import LexicalAnalyzer
import re


class MyParser:
    INVALID_LEXEME_CODE = 0
    # std::complex<double> my_complex(-10.0, 2.0);
    EXPECTED_TOKEN_SEQUENCE = [
        "KEYWORD_STD",
        "DOUBLE_COLON",
        "KEYWORD_COMPLEX",
        "OPEN_ANGLE",
        "KEYWORD_DOUBLE",
        "CLOSE_ANGLE",
        "IDENTIFIER",
        "OPEN_PAREN",
        "FLOAT",
        "COMMA",
        "FLOAT",
        "CLOSE_PAREN",
        "SEMICOLON",
    ]

    def __init__(self, lang):
        self.lang = lang
        self.errors = []
        self.tokens = []
        self.token_types = {}

    def parse(self, text):
        lexer = LexicalAnalyzer(self.lang)
        raw_tokens, lex_errors = lexer.analyze(text)

        invalid_tokens = self._build_invalid_lexeme_tokens(lex_errors, text)
        self.tokens = self._merge_token_stream(raw_tokens, invalid_tokens)
        self.errors = []
        self.token_types = lexer.TOKEN_TYPES

        cursor = 0
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]

        while cursor < len(self.tokens):
            while cursor < len(self.tokens) and self.tokens[cursor]["code"] == space_code:
                cursor += 1
            if cursor >= len(self.tokens):
                break

            segment_end = self._find_line_end(cursor)
            self._parse_segment(cursor, segment_end)
            cursor = segment_end + 1

        return self.tokens, self.errors

    def _parse_segment(self, start, end):
        cursor = start
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        float_code = LexicalAnalyzer.TOKEN_CODES["FLOAT"]
        minus_code = LexicalAnalyzer.TOKEN_CODES["MINUS"]
        last_error_anchor = None

        for seq_index, token_name in enumerate(self.EXPECTED_TOKEN_SEQUENCE):
            expected_code = LexicalAnalyzer.TOKEN_CODES[token_name]
            check_spaces = expected_code == space_code
            ignore_minus = expected_code == float_code

            found_index = self._find_from_cursor_in_range(
                expected_code,
                cursor,
                end,
                skip_spaces=not check_spaces,
                skip_minus=ignore_minus,
            )

            if found_index is None:
                if cursor <= end:
                    wrong_fragment = self.tokens[cursor]["lexeme"]
                    location = self.tokens[cursor]["location"]
                    error_anchor = cursor
                else:
                    wrong_fragment = ""
                    location = "EOF"
                    error_anchor = end + 1

                if error_anchor != last_error_anchor:
                    self._add_error(expected_code, wrong_fragment, location)
                    last_error_anchor = error_anchor
                if self._should_advance_cursor_in_range(cursor, seq_index, end):
                    cursor += 1
                continue

            if found_index > cursor:
                if check_spaces:
                    wrong_indices = list(range(cursor, found_index))
                else:
                    wrong_indices = [
                        i
                        for i in range(cursor, found_index)
                        if self.tokens[i]["code"] != space_code
                        and not (ignore_minus and self.tokens[i]["code"] == minus_code)
                    ]

                if wrong_indices:
                    wrong_fragment = "".join(
                        t["lexeme"] for t in self.tokens[wrong_indices[0] : wrong_indices[-1] + 1]
                    )
                    location = self._range_location(wrong_indices[0], wrong_indices[-1])
                    error_anchor = wrong_indices[0]
                    if error_anchor != last_error_anchor:
                        self._add_error(expected_code, wrong_fragment, location)
                        last_error_anchor = error_anchor
                else:
                    last_error_anchor = None
            else:
                last_error_anchor = None

            cursor = found_index + 1

    def _find_line_end(self, start):
        start_line, _, _ = self._extract_location(self.tokens[start].get("location", ""))
        if start_line is None:
            return len(self.tokens) - 1

        for i in range(start, len(self.tokens)):
            line, _, _ = self._extract_location(self.tokens[i].get("location", ""))
            if line is None:
                continue
            if line != start_line:
                return i - 1
        return len(self.tokens) - 1

    def _build_invalid_lexeme_tokens(self, lex_errors, source_text):
        if not lex_errors:
            return []

        merged_tokens = []
        current = None
        lines = source_text.splitlines() or [source_text]

        for err in lex_errors:
            line, start_col, end_col = self._extract_location(err.get("location", ""))
            if line is None:
                current = None
                continue

            if current is None:
                current = {
                    "code": "ERROR",
                    "type": err.get("type", self.lang.translate("invalid_char")),
                    "lexeme": err.get("lexeme", ""),
                    "line": line,
                    "start_col": start_col,
                    "end_col": end_col,
                }
                continue

            is_adjacent = line == current["line"] and start_col == current["end_col"] + 1
            is_separated_by_spaces = False
            between_text = ""
            if line == current["line"] and start_col > current["end_col"] + 1:
                line_text = lines[line - 1] if 1 <= line <= len(lines) else ""
                between_text = line_text[current["end_col"] : start_col - 1]
                is_separated_by_spaces = between_text != "" and all(ch == " " for ch in between_text)

            if is_adjacent:
                current["lexeme"] += err.get("lexeme", "")
                current["end_col"] = end_col
            elif is_separated_by_spaces:
                current["lexeme"] += between_text + err.get("lexeme", "")
                current["end_col"] = end_col
            else:
                merged_tokens.append(
                    {
                        "code": self.INVALID_LEXEME_CODE,
                        "type": current["type"],
                        "lexeme": current["lexeme"],
                        "location": f"{self.lang.translate('line_num').format(current['line'], 0)}, "
                        f"{current['start_col']}-{current['end_col']}",
                    }
                )
                current = {
                    "code": "ERROR",
                    "type": err.get("type", self.lang.translate("invalid_char")),
                    "lexeme": err.get("lexeme", ""),
                    "line": line,
                    "start_col": start_col,
                    "end_col": end_col,
                }

        if current is not None:
            merged_tokens.append(
                {
                    "code": self.INVALID_LEXEME_CODE,
                    "type": current["type"],
                    "lexeme": current["lexeme"],
                    "location": f"{self.lang.translate('line_num').format(current['line'], 0)}, "
                    f"{current['start_col']}-{current['end_col']}",
                }
            )

        return merged_tokens

    def _merge_token_stream(self, raw_tokens, invalid_tokens):
        stream = list(raw_tokens) + list(invalid_tokens)
        stream.sort(key=self._token_sort_key)
        return stream

    def _token_sort_key(self, token):
        line, start_col, _ = self._extract_location(token.get("location", ""))
        if line is None:
            return (10**9, 10**9)
        return (line, start_col)

    def _find_from_cursor_in_range(
        self,
        expected_code,
        cursor,
        end,
        skip_spaces=False,
        skip_minus=False,
    ):
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        minus_code = LexicalAnalyzer.TOKEN_CODES["MINUS"]

        for i in range(cursor, end + 1):
            if skip_spaces and self.tokens[i]["code"] == space_code:
                continue
            if skip_minus and self.tokens[i]["code"] == minus_code:
                continue
            if self.tokens[i]["code"] == expected_code:
                return i
        return None

    def _should_advance_cursor_in_range(self, cursor, seq_index, end):
        if cursor > end or cursor >= len(self.tokens):
            return True

        future_expected_codes = {
            LexicalAnalyzer.TOKEN_CODES[name]
            for name in self.EXPECTED_TOKEN_SEQUENCE[seq_index + 1 :]
        }

        current_code = self.tokens[cursor]["code"]
        identifier_code = LexicalAnalyzer.TOKEN_CODES["IDENTIFIER"]

        if current_code == self.INVALID_LEXEME_CODE:
            return True

        if current_code == identifier_code:
            return True

        if current_code in future_expected_codes:
            return False

        next_idx = cursor + 1
        if next_idx <= end and next_idx < len(self.tokens):
            next_code = self.tokens[next_idx]["code"]
            if next_code in future_expected_codes:
                return False

        return True

    def _add_error(self, expected_code, wrong_fragment, location):
        expected_name = self.token_types[expected_code]
        self.errors.append(
            {
                "code": "ERROR",
                "type": f"{self.lang.translate('expected').format(expected_name)}",
                "lexeme": wrong_fragment,
                "location": location,
            }
        )

    def _range_location(self, start_idx, end_idx):
        if not self.tokens or start_idx < 0 or end_idx < 0 or start_idx >= len(self.tokens):
            return "EOF"
        if end_idx >= len(self.tokens):
            end_idx = len(self.tokens) - 1
        if start_idx > end_idx:
            last = self.tokens[-1]
            return f"{last['location']}, EOF"

        start = self.tokens[start_idx]
        end = self.tokens[end_idx]
        s_line, s_col, _ = self._extract_location(start["location"])
        e_line, _, e_col = self._extract_location(end["location"])

        if s_line is None or e_line is None:
            return start["location"]
        if s_line == e_line:
            return f"{self.lang.translate('line_num').format(s_line, 0)}, {s_col}-{e_col}"
        return f"{self.lang.translate('line_num').format(s_line, 0)}-{e_line}, {s_col}-{e_col}"

    @staticmethod
    def _extract_location(location):
        numbers = re.findall(r"\d+", location or "")
        if len(numbers) < 3:
            return None, None, None
        return int(numbers[0]), int(numbers[1]), int(numbers[2])
