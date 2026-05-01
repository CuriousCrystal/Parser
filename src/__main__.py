from __future__ import annotations

import sys

from .lexer import Lexer
from .parser import Parser, ParseError
from .semantic import SemanticAnalyzer
from .codegen import CodeGenerator


def main(path: str) -> int:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            source = handle.read()
    except OSError as exc:
        print(f"Unable to read file: {exc}")
        return 1

    lexer = Lexer(source)
    parser = Parser(lexer)
    try:
        program = parser.parse_program()
    except ParseError as exc:
        print(exc)
        return 1

    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(program)
    if errors:
        for error in errors:
            print(f"Semantic error: {error}")
        return 1

    generator = CodeGenerator()
    ir = generator.generate(program)
    print(ir)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src <source-file.c>")
        sys.exit(1)
    sys.exit(main(sys.argv[1]))
