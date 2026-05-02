from __future__ import annotations

import argparse
import sys

from .lexer import Lexer
from .parser import Parser, ParseError
from .semantic import SemanticAnalyzer
from .codegen import CodeGenerator
from .visualize import ast_to_mermaid


def main(path: str, visualize: bool) -> int:
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

    if visualize:
        diagram = ast_to_mermaid(program)
        print(diagram)
    else:
        print(ir)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile a C-like source file and optionally visualize the AST.")
    parser.add_argument("source", help="Source file path")
    parser.add_argument("--visualize-ast", action="store_true", help="Output AST visualization as Mermaid diagram")
    args = parser.parse_args()

    sys.exit(main(args.source, args.visualize_ast))
