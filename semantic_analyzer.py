from decimal import Decimal, InvalidOperation
import re

from lexer import LexicalAnalyzer


class AstNode:
    def __init__(self, node_type, attributes=None):
        self.node_type = node_type
        self.attributes = attributes or {}
        self.children = []

    def add_child(self, label, node):
        self.children.append((label, node))


class SymbolTable:
    def __init__(self):
        self._symbols = {}

    def declare(self, name, type_name, value, location):
        if self.check_duplicate(name):
            return False
        self._symbols[name] = {
            "name": name,
            "type": type_name,
            "value": value,
            "location": location,
        }
        return True

    def lookup(self, name):
        return self._symbols.get(name)

    def check_duplicate(self, name):
        return name in self._symbols


class SemanticAnalyzer:
    DOUBLE_MAX = Decimal("1.7976931348623157e308")
    DOUBLE_MIN_SUBNORMAL = Decimal("4.9406564584124654e-324")

    def __init__(self, lang):
        self.lang = lang
        self.errors = []
        self.symbol_table = SymbolTable()
        self.ast_nodes = []

    def analyze(self, text, ast_blocked_lines=None):
        lexer = LexicalAnalyzer(self.lang)
        tokens, _ = lexer.analyze(text)

        self.errors = []
        self.symbol_table = SymbolTable()
        self.ast_nodes = []
        blocked = set(ast_blocked_lines or set())

        lines = self._split_tokens_by_line(tokens)
        for line_no, line_tokens in lines:
            line_errors_before = len(self.errors)
            node = self._analyze_line(line_tokens)
            line_has_semantic_errors = len(self.errors) > line_errors_before
            if node is not None and not line_has_semantic_errors and line_no not in blocked:
                self.ast_nodes.append(node)

        ast_text = self._format_ast()
        return self.errors, ast_text

    def _analyze_line(self, line_tokens):
        significant = [t for t in line_tokens if t["code"] != LexicalAnalyzer.TOKEN_CODES["SPACE"]]
        if not significant:
            return None

        code = LexicalAnalyzer.TOKEN_CODES
        try:
            std_idx = self._find_index(significant, code["KEYWORD_STD"])
            double_colon_idx = self._find_index(significant, code["DOUBLE_COLON"], start=std_idx + 1)
            complex_idx = self._find_index(significant, code["KEYWORD_COMPLEX"], start=double_colon_idx + 1)
            open_angle_idx = self._find_index(significant, code["OPEN_ANGLE"], start=complex_idx + 1)
            type_idx = self._find_index(significant, code["KEYWORD_DOUBLE"], start=open_angle_idx + 1)
            close_angle_idx = self._find_index(significant, code["CLOSE_ANGLE"], start=type_idx + 1)
            identifier_idx = self._find_index(significant, code["IDENTIFIER"], start=close_angle_idx + 1)
            open_paren_idx = self._find_index(significant, code["OPEN_PAREN"], start=identifier_idx + 1)
            close_paren_idx = self._find_index(significant, code["CLOSE_PAREN"], start=open_paren_idx + 1)
        except ValueError:
            return None

        identifier_token = significant[identifier_idx]
        identifier = identifier_token["lexeme"]
        line_has_error = False
        is_duplicate = False

        if self.symbol_table.check_duplicate(identifier):
            existing = self.symbol_table.lookup(identifier)
            first_line, _, _ = self._extract_location(existing["location"])
            self.errors.append(
                {
                    "analysis_type": "semantic",
                    "semantic_code": "DUPLICATE_IDENTIFIER",
                    "lexeme": identifier,
                    "description": self.lang.translate("semantic_duplicate_identifier").format(
                        identifier,
                        first_line if first_line is not None else "?",
                    ),
                    "location": identifier_token["location"],
                }
            )
            line_has_error = True
            is_duplicate = True

        values, value_locations = self._extract_values(significant, open_paren_idx + 1, close_paren_idx - 1)

        for value_text, location_text in zip(values, value_locations):
            raw_value = value_text[1:] if value_text.startswith("-") else value_text
            is_negative = value_text.startswith("-")
            is_float = "." in raw_value

            if not is_float:
                self.errors.append(
                    {
                        "analysis_type": "semantic",
                        "semantic_code": "TYPE_MISMATCH",
                        "lexeme": raw_value,
                        "description": self.lang.translate("semantic_type_mismatch").format(raw_value),
                        "location": location_text,
                    }
                )
                line_has_error = True

            if not self._is_double_value_in_range(raw_value, is_negative):
                preview = self._build_short_value_preview(raw_value, is_negative)
                self.errors.append(
                    {
                        "analysis_type": "semantic",
                        "semantic_code": "OUT_OF_RANGE",
                        "lexeme": preview,
                        "description": self.lang.translate("semantic_out_of_range").format(preview),
                        "location": location_text,
                    }
                )
                line_has_error = True

        if not is_duplicate:
            self.symbol_table.declare(
                name=identifier,
                type_name="double",
                value=values,
                location=identifier_token["location"],
            )

        if line_has_error:
            return None
        return self._build_complex_decl_ast(identifier, values)

    @staticmethod
    def _find_index(tokens, target_code, start=0):
        for idx in range(start, len(tokens)):
            if tokens[idx]["code"] == target_code:
                return idx
        raise ValueError("Token not found")

    def _extract_values(self, tokens, start_idx, end_idx):
        values = []
        locations = []
        minus_code = LexicalAnalyzer.TOKEN_CODES["MINUS"]
        integer_code = LexicalAnalyzer.TOKEN_CODES["INTEGER"]
        float_code = LexicalAnalyzer.TOKEN_CODES["FLOAT"]

        prev_token = None
        for idx in range(start_idx, end_idx + 1):
            token = tokens[idx]
            token_code = token["code"]
            if token_code not in (integer_code, float_code):
                prev_token = token
                continue

            is_negative = prev_token is not None and prev_token["code"] == minus_code
            text = f"-{token['lexeme']}" if is_negative else token["lexeme"]
            values.append(text)
            locations.append(token["location"])
            prev_token = token

        return values, locations

    @staticmethod
    def _build_complex_decl_ast(name, values):
        decl = AstNode(
            "ComplexDeclNode",
            {
                "name": f"\"{name}\"",
                "modifiers": "[\"std\", \"complex\"]",
            },
        )
        type_node = AstNode("DoubleNode", {"name": "\"double\""})
        values_node = AstNode("DoubleLiteralNode", {"value": f"[{', '.join(values)}]"})

        decl.add_child("type", type_node)
        decl.add_child("values", values_node)
        return decl

    def _format_ast(self):
        if not self.ast_nodes:
            return self.lang.translate("ast_not_available")

        rendered = []
        for node in self.ast_nodes:
            lines = [node.node_type]
            self._render_entries(node, "", lines)
            rendered.append("\n".join(lines))
        return "\n\n".join(rendered)

    def _render_entries(self, node, prefix, out_lines):
        entries = []
        for key, value in node.attributes.items():
            entries.append(("attr", key, value))
        for label, child in node.children:
            entries.append(("child", label, child))

        for idx, entry in enumerate(entries):
            is_last = idx == len(entries) - 1
            branch = "└── " if is_last else "├── "
            if entry[0] == "attr":
                _, key, value = entry
                out_lines.append(f"{prefix}{branch}{key}: {value}")
                continue

            _, label, child = entry
            out_lines.append(f"{prefix}{branch}{label}: {child.node_type}")
            next_prefix = prefix + ("    " if is_last else "│   ")
            self._render_entries(child, next_prefix, out_lines)

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
