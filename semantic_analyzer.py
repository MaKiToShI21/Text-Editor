from parser import ParseSession, Parser


class SemanticAnalyzer:
    def __init__(self, lang):
        self.lang = lang

    def analyze_full(self, text):
        """Lexical + syntax + IR in one pass (no duplicate parsing)."""
        parser = Parser(self.lang)
        session = parser.analyze(text, collect_ir=True)
        report = self.format_ir_report(session)
        return session, report

    def format_ir_report(self, session: ParseSession) -> str:
        lines: list[str] = []
        if session.errors:
            lines.append(self.lang.translate("ir_skipped_due_to_errors"))
            lines.append("")

        # lines.append(self.lang.translate("ir_report_title"))
        # lines.append("")

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
                lines.append(f"{self.lang.translate('ir_value')}: {lr.value or self.lang.translate('value_not_available')}")
            else:
                lines.append(f"  {self.lang.translate('poliz_not_available')}")
            lines.append("")

        return "\n".join(lines).rstrip()
