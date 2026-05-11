from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple


# AST
@dataclass
class AstNode:
    node_type: str
    attributes: dict = field(default_factory=dict)
    children: List[Tuple[str, "AstNode"]] = field(default_factory=list)

    def add_child(self, label: str, node: "AstNode") -> None:
        self.children.append((label, node))


def build_complex_decl_ast(name: str, real_value: str, imag_value: str) -> AstNode:
    decl = AstNode(
        "ComplexDeclNode",
        {
            "name": f"\"{name}\"",
            "modifiers": "[\"std\", \"complex\"]",
        },
    )
    type_node = AstNode("DoubleNode", {"name": "\"double\""})
    real_node = _build_value_node("real", real_value)
    imag_node = _build_value_node("imag", imag_value)

    decl.add_child("type", type_node)
    decl.add_child("real", real_node)
    decl.add_child("imag", imag_node)
    return decl


def _build_value_node(label: str, value_text: str) -> AstNode:
    """Сформировать поддерево для конкретного значения"""

    if value_text.startswith("-"):
        unary = AstNode("UnaryOpNode", {"op": "\"-\""})
        unary.add_child(
            "operand",
            AstNode("DoubleLiteralNode", {"value": value_text[1:]}),
        )
        return unary
    return AstNode("DoubleLiteralNode", {"value": value_text})


def format_ast(node: AstNode) -> str:
    lines = [node.node_type]
    _render_entries(node, "", lines)
    return "\n".join(lines)


def _render_entries(node: AstNode, prefix: str, out_lines: List[str]) -> None:
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
        _render_entries(child, next_prefix, out_lines)


# Промежуточное представление (TAC)
@dataclass
class TacInstr:
    op: str
    target: str
    arg1: Optional[str] = None
    arg2: Optional[str] = None
    field: Optional[str] = None
    extra: Optional[str] = None

    def render(self) -> str:
        target = f"{self.target}.{self.field}" if self.field else self.target

        if self.op == "const":
            return f"{target} = {self.arg1}"
        if self.op == "neg":
            return f"{target} = neg {self.arg1}"
        if self.op == "copy":
            return f"{target} = {self.arg1}"
        if self.op == "store":
            return f"{target} = {self.arg1}"
        if self.op == "call":
            return f"{target} = call {self.extra}({self.arg1}, {self.arg2})"
        if self.op == "binop":
            return f"{target} = {self.arg1} {self.extra} {self.arg2}"
        return f"{target} = ??? ({self.op})"


def render_tac(instructions: List[TacInstr]) -> str:
    if not instructions:
        return "<пусто>"
    return "\n".join(instr.render() for instr in instructions)


# Генератор IR
class IRGenerator:
    def __init__(self) -> None:
        self._counter = 0

    def _fresh(self) -> str:
        self._counter += 1
        return f"t{self._counter}"

    def generate(self, name: str, real_value: str, imag_value: str) -> List[TacInstr]:
        """Сгенерировать TAC по строковым значениям real/imag"""

        self._counter = 0
        instructions: List[TacInstr] = []

        real_temp = self._emit_value(instructions, real_value)
        imag_temp = self._emit_value(instructions, imag_value)

        copy_real = self._fresh()
        instructions.append(TacInstr(op="copy", target=copy_real, arg1=real_temp))

        copy_imag = self._fresh()
        instructions.append(TacInstr(op="copy", target=copy_imag, arg1=imag_temp))

        instructions.append(
            TacInstr(op="store", target=name, field="real", arg1=copy_real)
        )
        instructions.append(
            TacInstr(op="store", target=name, field="imag", arg1=copy_imag)
        )
        return instructions

    def _emit_value(self, instructions: List[TacInstr], value: str) -> str:
        """Эмитировать инструкции для числового значения, вернуть имя temp"""

        if value.startswith("-"):
            literal_temp = self._fresh()
            instructions.append(
                TacInstr(op="const", target=literal_temp, arg1=value[1:])
            )
            neg_temp = self._fresh()
            instructions.append(
                TacInstr(op="neg", target=neg_temp, arg1=literal_temp)
            )
            return neg_temp

        literal_temp = self._fresh()
        instructions.append(TacInstr(op="const", target=literal_temp, arg1=value))
        return literal_temp


# Оптимизации
class ConstantFoldingOptimizer:
    """Локальная оптимизация: свёртка констант"""

    BINARY_OPS = {"+": "add", "-": "sub", "*": "mul", "/": "div"}

    def optimize(self, instructions: List[TacInstr]) -> List[TacInstr]:
        constants: dict[str, str] = {}
        result: List[TacInstr] = []

        for instr in instructions:
            new_instr = self._fold(instr, constants)
            result.append(new_instr)

            if new_instr.op == "const" and new_instr.target.startswith("t"):
                constants[new_instr.target] = new_instr.arg1 or ""
            elif new_instr.op == "copy" and new_instr.target.startswith("t"):
                if new_instr.arg1 in constants:
                    constants[new_instr.target] = constants[new_instr.arg1]

        return result

    def _fold(self, instr: TacInstr, constants: dict[str, str]) -> TacInstr:
        if instr.op == "neg" and instr.arg1 in constants:
            folded = self._negate(constants[instr.arg1])
            if folded is not None:
                return TacInstr(op="const", target=instr.target, arg1=folded)

        if instr.op == "binop" and instr.arg1 in constants and instr.arg2 in constants:
            folded = self._fold_binary(
                constants[instr.arg1], instr.extra or "+", constants[instr.arg2]
            )
            if folded is not None:
                return TacInstr(op="const", target=instr.target, arg1=folded)

        return instr

    @staticmethod
    def _negate(value: str) -> Optional[str]:
        try:
            decimal = Decimal(value)
        except InvalidOperation:
            return None
        negated = -decimal
        return _format_number(negated)

    @classmethod
    def _fold_binary(cls, lhs: str, op: str, rhs: str) -> Optional[str]:
        try:
            left = Decimal(lhs)
            right = Decimal(rhs)
        except InvalidOperation:
            return None
        try:
            if op == "+":
                value = left + right
            elif op == "-":
                value = left - right
            elif op == "*":
                value = left * right
            elif op == "/":
                if right == 0:
                    return None
                value = left / right
            else:
                return None
        except (InvalidOperation, ZeroDivisionError):
            return None
        return _format_number(value)


class CopyPropagationOptimizer:
    """Удаление лишних копий + устранение мёртвого кода + канонизация"""

    def optimize(self, instructions: List[TacInstr]) -> List[TacInstr]:
        propagated = self._propagate(instructions)
        simplified = [self._algebraic_simplify(instr) for instr in propagated]
        return self._eliminate_dead(simplified)

    @staticmethod
    def _propagate(instructions: List[TacInstr]) -> List[TacInstr]:
        aliases: dict[str, str] = {}

        result: List[TacInstr] = []
        for instr in instructions:
            new_arg1 = aliases.get(instr.arg1, instr.arg1) if instr.arg1 else instr.arg1
            new_arg2 = aliases.get(instr.arg2, instr.arg2) if instr.arg2 else instr.arg2
            new_instr = TacInstr(
                op=instr.op,
                target=instr.target,
                arg1=new_arg1,
                arg2=new_arg2,
                field=instr.field,
                extra=instr.extra,
            )
            result.append(new_instr)

            if new_instr.op == "copy" and new_instr.target.startswith("t"):
                aliases[new_instr.target] = new_arg1 or new_instr.target
            elif new_instr.op == "const" and new_instr.target.startswith("t"):
                aliases[new_instr.target] = new_arg1 or ""

        return result

    @staticmethod
    def _algebraic_simplify(instr: TacInstr) -> TacInstr:
        if instr.op != "binop":
            return instr

        op = instr.extra or ""
        if op == "+":
            if _is_zero(instr.arg1):
                return TacInstr(op="copy", target=instr.target, arg1=instr.arg2)
            if _is_zero(instr.arg2):
                return TacInstr(op="copy", target=instr.target, arg1=instr.arg1)
        elif op == "-":
            if _is_zero(instr.arg2):
                return TacInstr(op="copy", target=instr.target, arg1=instr.arg1)
        elif op == "*":
            if _is_one(instr.arg1):
                return TacInstr(op="copy", target=instr.target, arg1=instr.arg2)
            if _is_one(instr.arg2):
                return TacInstr(op="copy", target=instr.target, arg1=instr.arg1)
            if _is_zero(instr.arg1) or _is_zero(instr.arg2):
                return TacInstr(op="const", target=instr.target, arg1="0.0")
        elif op == "/":
            if _is_one(instr.arg2):
                return TacInstr(op="copy", target=instr.target, arg1=instr.arg1)
        return instr

    @staticmethod
    def _eliminate_dead(instructions: List[TacInstr]) -> List[TacInstr]:
        uses: dict[str, int] = {}
        for instr in instructions:
            for arg in (instr.arg1, instr.arg2):
                if arg is None:
                    continue
                if arg.startswith("t"):
                    uses[arg] = uses.get(arg, 0) + 1

        survivors: List[TacInstr] = []
        for instr in instructions:
            if instr.op == "store":
                survivors.append(instr)
                continue
            target = instr.target
            if target and target.startswith("t") and uses.get(target, 0) == 0:
                continue
            survivors.append(instr)

        # Канонизация: если последняя инструкция перед store содержит лишь
        # копию из временной переменной, которая больше нигде не нужна, —
        # склеиваем такое присваивание (повторяем до устойчивости).
        return _inline_single_use(survivors)


def _inline_single_use(instructions: List[TacInstr]) -> List[TacInstr]:
    """Подставить значение временной переменной, используемой ровно один раз."""

    while True:
        uses: dict[str, int] = {}
        defs: dict[str, TacInstr] = {}
        for instr in instructions:
            for arg in (instr.arg1, instr.arg2):
                if arg and arg.startswith("t"):
                    uses[arg] = uses.get(arg, 0) + 1
            if instr.target and instr.target.startswith("t"):
                defs[instr.target] = instr

        changed = False
        new_instructions: List[TacInstr] = []
        consumed: set[str] = set()

        for instr in instructions:
            if instr.target in consumed:
                continue

            new_arg1 = instr.arg1
            new_arg2 = instr.arg2

            if (
                instr.arg1
                and instr.arg1.startswith("t")
                and uses.get(instr.arg1, 0) == 1
                and instr.arg1 in defs
                and defs[instr.arg1].op == "const"
            ):
                new_arg1 = defs[instr.arg1].arg1
                consumed.add(instr.arg1)
                changed = True

            if (
                instr.arg2
                and instr.arg2.startswith("t")
                and uses.get(instr.arg2, 0) == 1
                and instr.arg2 in defs
                and defs[instr.arg2].op == "const"
            ):
                new_arg2 = defs[instr.arg2].arg1
                consumed.add(instr.arg2)
                changed = True

            new_instructions.append(
                TacInstr(
                    op=instr.op,
                    target=instr.target,
                    arg1=new_arg1,
                    arg2=new_arg2,
                    field=instr.field,
                    extra=instr.extra,
                )
            )

        instructions = [i for i in new_instructions if i.target not in consumed]
        if not changed:
            break

    return instructions


# Утилиты
def _is_zero(value: Optional[str]) -> bool:
    if value is None or value.startswith("t"):
        return False
    try:
        return Decimal(value) == 0
    except InvalidOperation:
        return False


def _is_one(value: Optional[str]) -> bool:
    if value is None or value.startswith("t"):
        return False
    try:
        return Decimal(value) == 1
    except InvalidOperation:
        return False


def _format_number(value: Decimal) -> str:
    text = format(value, "f")
    if "." not in text:
        return f"{text}.0"
    text = text.rstrip("0").rstrip(".")
    if "." not in text:
        return f"{text}.0"
    return text


COMPLEX_DECL_RE = re.compile(
    r"""
    \bstd\s*::\s*complex\s*<\s*double\s*>\s*
    (?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*
    \(\s*
        (?P<real>-?\s*\d+(?:\.\d+)?)\s*
        ,\s*
        (?P<imag>-?\s*\d+(?:\.\d+)?)\s*
    \)\s*;
    """,
    re.VERBOSE,
)


@dataclass
class OptimizationPipelineResult:
    name: str
    real: str
    imag: str
    ast: AstNode
    ast_text: str
    initial_tac: List[TacInstr]
    after_constant_folding: List[TacInstr]
    after_copy_propagation: List[TacInstr]

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "real": self.real,
            "imag": self.imag,
            "ast_text": self.ast_text,
            "initial_tac": render_tac(self.initial_tac),
            "after_constant_folding": render_tac(self.after_constant_folding),
            "after_copy_propagation": render_tac(self.after_copy_propagation),
        }


def run_optimization_pipeline(source_line: str) -> Optional[OptimizationPipelineResult]:
    """Полный конвейер: разбор → AST → IR → две оптимизации.

    Возвращает None, если в строке не распознана нужная конструкция.
    Семантика конструкции сохраняется на всех этапах преобразования.
    """

    match = COMPLEX_DECL_RE.search(source_line)
    if match is None:
        return None

    name = match.group("name")
    real = _normalize_value(match.group("real"))
    imag = _normalize_value(match.group("imag"))

    ast = build_complex_decl_ast(name, real, imag)
    ast_text = format_ast(ast)

    initial_tac = IRGenerator().generate(name, real, imag)
    after_cf = ConstantFoldingOptimizer().optimize(initial_tac)
    after_cp = CopyPropagationOptimizer().optimize(after_cf)

    return OptimizationPipelineResult(
        name=name,
        real=real,
        imag=imag,
        ast=ast,
        ast_text=ast_text,
        initial_tac=initial_tac,
        after_constant_folding=after_cf,
        after_copy_propagation=after_cp,
    )


def _normalize_value(raw: str) -> str:
    """Удалить пробелы (например, между минусом и цифрой) из значения."""

    cleaned = re.sub(r"\s+", "", raw)
    if cleaned.startswith("-"):
        body = cleaned[1:]
        if "." not in body:
            body = f"{body}.0"
        return f"-{body}"
    if "." not in cleaned:
        cleaned = f"{cleaned}.0"
    return cleaned
