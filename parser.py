from lexer import LexicalAnalyzer
import re


class Parser:
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
        close_angle_code = LexicalAnalyzer.TOKEN_CODES["CLOSE_ANGLE"]
        identifier_code = LexicalAnalyzer.TOKEN_CODES["IDENTIFIER"]
        keyword_std_code = LexicalAnalyzer.TOKEN_CODES["KEYWORD_STD"]
        keyword_complex_code = LexicalAnalyzer.TOKEN_CODES["KEYWORD_COMPLEX"]
        double_colon_code = LexicalAnalyzer.TOKEN_CODES["DOUBLE_COLON"]
        open_angle_code = LexicalAnalyzer.TOKEN_CODES["OPEN_ANGLE"]
        integer_code = LexicalAnalyzer.TOKEN_CODES["INTEGER"]
        keyword_double_code = LexicalAnalyzer.TOKEN_CODES["KEYWORD_DOUBLE"]
        open_paren_code = LexicalAnalyzer.TOKEN_CODES["OPEN_PAREN"]
        close_paren_code = LexicalAnalyzer.TOKEN_CODES["CLOSE_PAREN"]
        comma_code = LexicalAnalyzer.TOKEN_CODES["COMMA"]
        semicolon_code = LexicalAnalyzer.TOKEN_CODES["SEMICOLON"]
        recovery_anchor_codes = {open_angle_code, open_paren_code}
        suppress_cascade_errors = False
        recovery_matches = 0
        previous_expected_code = None
        previous_found_index = None
        semicolon_index = None

        for seq_index, token_name in enumerate(self.EXPECTED_TOKEN_SEQUENCE):
            expected_code = LexicalAnalyzer.TOKEN_CODES[token_name]
            check_spaces = expected_code == space_code
            ignore_minus = expected_code == float_code

            if expected_code == float_code:
                first_idx = self._find_nearest_significant_token(
                    cursor,
                    end,
                    skip_minus=False,
                )
                if first_idx is not None:
                    token_code = self.tokens[first_idx]["code"]
                    probe_idx = first_idx
                    if token_code == minus_code:
                        scan_idx = first_idx + 1
                        while scan_idx <= end and self.tokens[scan_idx]["code"] == space_code:
                            scan_idx += 1

                        extra_start_idx = None
                        extra_end_idx = None
                        while scan_idx <= end and self.tokens[scan_idx]["code"] == minus_code:
                            if extra_start_idx is None:
                                extra_start_idx = scan_idx
                            extra_end_idx = scan_idx
                            scan_idx += 1

                        if extra_start_idx is not None and extra_end_idx is not None:
                            wrong_fragment = "".join(
                                t["lexeme"] for t in self.tokens[extra_start_idx : extra_end_idx + 1]
                            )
                            location = self._range_location(extra_start_idx, extra_end_idx)
                            # Лишние минусы после первого корректного считаем одной ошибкой-диапазоном.
                            self._add_error(expected_code, wrong_fragment, location)
                            # Остаёмся в шаге FLOAT, чтобы текущее число (например, 10.0)
                            # распозналось как значение после лишних минусов.
                            suppress_cascade_errors = False
                        probe_idx = self._find_nearest_significant_token(
                            first_idx + 1,
                            end,
                            skip_minus=False,
                        )

                    if probe_idx is not None and self.tokens[probe_idx]["code"] == integer_code:
                        wrong_fragment = self.tokens[probe_idx]["lexeme"]
                        location = self.tokens[probe_idx]["location"]
                        if not suppress_cascade_errors:
                            self._add_error(expected_code, wrong_fragment, location)

                        previous_expected_code = expected_code
                        previous_found_index = None
                        recovery_matches = 0
                        if not self._has_significant_tokens_after(probe_idx, end):
                            break
                        cursor = probe_idx + 1
                        continue

            found_index = self._find_from_cursor_in_range(
                expected_code,
                cursor,
                end,
                skip_spaces=not check_spaces,
                skip_minus=ignore_minus,
            )

            if found_index is None:
                if cursor <= end:
                    offending_idx = cursor
                    if expected_code == keyword_complex_code:
                        merged = self._collect_adjacent_identifier_invalid_fragment(cursor, end)
                        if merged is not None:
                            offending_idx, merged_end, merged_lexeme = merged
                            wrong_fragment = merged_lexeme
                            location = self._range_location(offending_idx, merged_end)
                        else:
                            wrong_fragment = self.tokens[offending_idx]["lexeme"]
                            location = self.tokens[offending_idx]["location"]
                    else:
                        wrong_fragment = self.tokens[offending_idx]["lexeme"]
                        location = self.tokens[offending_idx]["location"]

                    if self.tokens[cursor]["code"] == space_code and not check_spaces:
                        nearest_idx = self._find_nearest_significant_token(
                            cursor,
                            end,
                            skip_minus=ignore_minus,
                        )
                        if nearest_idx is not None:
                            offending_idx = nearest_idx
                            if expected_code != keyword_complex_code:
                                wrong_fragment = self.tokens[offending_idx]["lexeme"]
                                location = self.tokens[offending_idx]["location"]

                    # В начале разбора и при ожидании "::" хотим показывать весь хвост,
                    # если строка больше не содержит структурного якоря "<".
                    if (
                        expected_code in (keyword_std_code, double_colon_code)
                        and self.tokens[offending_idx]["code"] == identifier_code
                        and self._tail_is_identifier_chain(offending_idx, end)
                    ):
                        wrong_fragment = "".join(t["lexeme"] for t in self.tokens[offending_idx : end + 1])
                        location = self._range_location(offending_idx, end)
                else:
                    wrong_fragment = "EOF"
                    location = "EOF"

                if (
                    expected_code == comma_code
                    and cursor <= end
                    and self.tokens[cursor]["code"] == close_paren_code
                ):
                    if self._should_advance_cursor_in_range(cursor, seq_index, end):
                        cursor += 1
                    continue

                force_emit = (
                    expected_code == open_angle_code
                    and previous_expected_code == keyword_complex_code
                    and previous_found_index is not None
                ) or (
                    expected_code == identifier_code
                    and previous_expected_code == close_angle_code
                    and previous_found_index is not None
                ) or (
                    expected_code == open_paren_code
                    and previous_expected_code == identifier_code
                    and previous_found_index is not None
                    and self._is_decl_identifier_context(previous_found_index)
                )

                if not suppress_cascade_errors or force_emit:
                    self._add_error(expected_code, wrong_fragment, location)
                suppress_cascade_errors = True
                recovery_matches = 0
                if self._should_advance_cursor_in_range(cursor, seq_index, end):
                    cursor += 1
                previous_expected_code = expected_code
                previous_found_index = None
                continue

            if (
                expected_code == identifier_code
                and previous_expected_code == close_angle_code
                and previous_found_index is not None
                and not self._has_space_between(previous_found_index, found_index)
            ):
                wrong_fragment = self.tokens[found_index]["lexeme"]
                location = self.tokens[found_index]["location"]
                if not suppress_cascade_errors or expected_code == identifier_code:
                    self._add_error(space_code, wrong_fragment, location)
                suppress_cascade_errors = True
                recovery_matches = 0

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
                    if not suppress_cascade_errors:
                        self._add_error(expected_code, wrong_fragment, location)
                    suppress_cascade_errors = True
                    recovery_matches = 0
                    if expected_code == open_angle_code:
                        suppress_cascade_errors = False
                    if expected_code == keyword_std_code:
                        suppress_cascade_errors = False
                    if expected_code == keyword_double_code:
                        suppress_cascade_errors = False
                    if expected_code == close_paren_code:
                        suppress_cascade_errors = False
                else:
                    if suppress_cascade_errors:
                        if expected_code in recovery_anchor_codes or expected_code in (
                            keyword_double_code,
                            close_paren_code,
                        ):
                            suppress_cascade_errors = False
                            recovery_matches = 0
                        elif (
                            expected_code == keyword_complex_code
                            and previous_expected_code == double_colon_code
                            and found_index == cursor
                        ) or (
                            expected_code == identifier_code
                            and previous_expected_code == close_angle_code
                            and found_index == cursor
                        ):
                            suppress_cascade_errors = False
                            recovery_matches = 0
                        else:
                            recovery_matches += 1
                            if recovery_matches >= 2:
                                suppress_cascade_errors = False
                                recovery_matches = 0
            else:
                if suppress_cascade_errors:
                    if expected_code in recovery_anchor_codes or expected_code in (
                        keyword_double_code,
                        close_paren_code,
                    ):
                        suppress_cascade_errors = False
                        recovery_matches = 0
                    elif (
                        expected_code == keyword_complex_code
                        and previous_expected_code == double_colon_code
                    ) or (
                        expected_code == identifier_code
                        and previous_expected_code == close_angle_code
                    ) or (
                        expected_code == double_colon_code
                        and previous_expected_code == keyword_std_code
                    ):
                        suppress_cascade_errors = False
                        recovery_matches = 0
                    else:
                        recovery_matches += 1
                        if recovery_matches >= 2:
                            suppress_cascade_errors = False
                            recovery_matches = 0

            previous_expected_code = expected_code
            previous_found_index = found_index
            if expected_code == semicolon_code:
                semicolon_index = found_index
            cursor = found_index + 1

        if semicolon_index is not None:
            trailing_idx = self._find_nearest_significant_token(
                semicolon_index + 1,
                end,
                skip_minus=False,
            )
            if trailing_idx is not None:
                wrong_fragment = "".join(t["lexeme"] for t in self.tokens[trailing_idx : end + 1])
                location = self._range_location(trailing_idx, end)
                self._add_invalid_fragment_error(wrong_fragment, location)

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

    def _find_nearest_significant_token(self, cursor, end, skip_minus=False):
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        minus_code = LexicalAnalyzer.TOKEN_CODES["MINUS"]

        for i in range(cursor, end + 1):
            code = self.tokens[i]["code"]
            if code == space_code:
                continue
            if skip_minus and code == minus_code:
                continue
            return i
        return None

    def _collect_adjacent_identifier_invalid_fragment(self, start_idx, end_idx):
        if start_idx > end_idx or start_idx >= len(self.tokens):
            return None

        identifier_code = LexicalAnalyzer.TOKEN_CODES["IDENTIFIER"]
        if self.tokens[start_idx]["code"] != identifier_code:
            return None

        current_end = start_idx
        parts = [self.tokens[start_idx]["lexeme"]]
        _, _, prev_end_col = self._extract_location(self.tokens[start_idx].get("location", ""))

        for i in range(start_idx + 1, end_idx + 1):
            code = self.tokens[i]["code"]
            if code not in (identifier_code, self.INVALID_LEXEME_CODE):
                break

            _, next_start_col, next_end_col = self._extract_location(self.tokens[i].get("location", ""))
            if prev_end_col is None or next_start_col is None:
                break
            if next_start_col != prev_end_col + 1:
                break

            parts.append(self.tokens[i]["lexeme"])
            current_end = i
            prev_end_col = next_end_col

        if current_end == start_idx:
            return None
        return start_idx, current_end, "".join(parts)

    def _contains_code_in_range(self, target_code, start, end):
        if start > end:
            return False
        for i in range(start, end + 1):
            if self.tokens[i]["code"] == target_code:
                return True
        return False

    def _has_significant_tokens_after(self, idx, end):
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        for i in range(idx + 1, end + 1):
            if self.tokens[i]["code"] != space_code:
                return True
        return False

    def _tail_is_identifier_chain(self, start, end):
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        identifier_code = LexicalAnalyzer.TOKEN_CODES["IDENTIFIER"]
        saw_identifier = False

        for i in range(start, end + 1):
            code = self.tokens[i]["code"]
            if code == space_code:
                continue
            if code != identifier_code:
                return False
            saw_identifier = True
        return saw_identifier

    def _has_space_between(self, left_idx, right_idx):
        if left_idx is None or right_idx is None or right_idx <= left_idx:
            return False

        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        for i in range(left_idx + 1, right_idx):
            if self.tokens[i]["code"] == space_code:
                return True
        return False

    def _is_decl_identifier_context(self, idx):
        if idx is None or idx <= 0 or idx >= len(self.tokens):
            return False

        prev_idx = idx - 1
        space_code = LexicalAnalyzer.TOKEN_CODES["SPACE"]
        close_angle_code = LexicalAnalyzer.TOKEN_CODES["CLOSE_ANGLE"]
        keyword_double_code = LexicalAnalyzer.TOKEN_CODES["KEYWORD_DOUBLE"]

        while prev_idx >= 0 and self.tokens[prev_idx]["code"] == space_code:
            prev_idx -= 1

        if prev_idx < 0:
            return False

        return self.tokens[prev_idx]["code"] in (close_angle_code, keyword_double_code)

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

    def _add_invalid_fragment_error(self, wrong_fragment, location):
        self.errors.append(
            {
                "code": "ERROR",
                "type": self.lang.translate("invalid_char"),
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
