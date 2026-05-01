"""Unified error handling for the parser-lexer project.

This module defines custom exception classes for different stages of compilation.
All exceptions include location information for better error reporting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .lexer import Token


class CompilerError(RuntimeError):
    """Base class for all compiler errors."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        location = f" at {line}:{column}" if line is not None and column is not None else ""
        super().__init__(f"{self.__class__.__name__}{location}: {message}")
        self.line = line
        self.column = column


class LexerError(CompilerError):
    """Error during lexical analysis."""

    def __init__(self, message: str, line: int, column: int):
        super().__init__(message, line, column)


class ParserError(CompilerError):
    """Error during parsing."""

    def __init__(self, message: str, token: Token):
        super().__init__(message, token.line, token.column)
        self.token = token


class SemanticError(CompilerError):
    """Error during semantic analysis."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message, line, column)


class CodeGenerationError(CompilerError):
    """Error during code generation."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None):
        super().__init__(message, line, column)