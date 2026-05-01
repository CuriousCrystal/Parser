"""Simple lexer for a subset of C.

The lexer reads a source string and produces a stream of ``Token`` objects.
Each token records its type, the original lexeme, and the line/column where it
appeared.  Errors are reported via ``LexerError`` which includes location
information.

Supported token categories:
    - Keywords (e.g. ``int``, ``return``)
    - Identifiers
    - Integer literals (decimal only for simplicity)
    - Operators and punctuators (``+ - * / = ; , ( ) { }`` etc.)
    - Single‑line ``//`` and multi‑line ``/* */`` comments (ignored)
    - Whitespace (ignored but used to track line/column numbers)

The implementation is deliberately straightforward – a single ``while`` loop
with helper methods for each lexical class.  It is sufficient for the parser
tests and can be extended later.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Generator

from .errors import LexerError


class TokenType(enum.Enum):
    EOF = "EOF"
    INT_LITERAL = "INT_LITERAL"
    IDENTIFIER = "IDENTIFIER"
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    PERCENT = "%"
    ASSIGN = "="
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    SEMICOLON = ";"
    COMMA = ","
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    DOT = "."
    ARROW = "->"
    AMP = "&"
    INT = "int"
    CHAR = "char"
    FLOAT = "float"
    VOID = "void"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    RETURN = "return"
    SIZEOF = "sizeof"
    STRUCT = "struct"
    TYPEDEF = "typedef"


KEYWORD_TOKENS = {
    "int": TokenType.INT,
    "char": TokenType.CHAR,
    "float": TokenType.FLOAT,
    "void": TokenType.VOID,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,
    "sizeof": TokenType.SIZEOF,
    "struct": TokenType.STRUCT,
    "typedef": TokenType.TYPEDEF,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.lexeme}', {self.line}:{self.column})"


class Lexer:
    """Iterates over the source text and yields :class:`Token` objects."""

    def __init__(self, source: str):
        self.source = source
        self.length = len(source)
        self.pos = 0
        self.line = 1
        self.column = 1

    # ---------------------------------------------------------------------
    # Helper utilities
    # ---------------------------------------------------------------------
    def _peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < self.length else "\0"

    def _advance(self) -> str:
        ch = self._peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def tokenize(self) -> Generator[Token, None, None]:
        while True:
            token = self._next_token()
            yield token
            if token.type == TokenType.EOF:
                break

    # ---------------------------------------------------------------------
    # Core token extraction logic
    # ---------------------------------------------------------------------
    def _skip_whitespace_and_comments(self) -> None:
        while True:
            ch = self._peek()
            if ch in " \t\r\n":
                self._advance()
                continue
            if ch == "/" and self._peek(1) == "/":
                self._advance(); self._advance()
                while self._peek() not in ("\n", "\0"):
                    self._advance()
                continue
            if ch == "/" and self._peek(1) == "*":
                self._advance(); self._advance()
                while not (self._peek() == "*" and self._peek(1) == "/"):
                    if self._peek() == "\0":
                        raise LexerError("Unterminated comment", self.line, self.column)
                    self._advance()
                self._advance(); self._advance()
                continue
            break

    def _next_token(self) -> Token:
        self._skip_whitespace_and_comments()
        start_line, start_col = self.line, self.column
        ch = self._peek()
        if ch == "\0":
            return Token(TokenType.EOF, "", start_line, start_col)
        # Identifier / keyword
        if ch.isalpha() or ch == "_":
            lex = []
            while self._peek().isalnum() or self._peek() == "_":
                lex.append(self._advance())
            text = "".join(lex)
            typ = KEYWORD_TOKENS.get(text, TokenType.IDENTIFIER)
            return Token(typ, text, start_line, start_col)
        # Integer literal
        if ch.isdigit():
            lex = []
            while self._peek().isdigit():
                lex.append(self._advance())
            return Token(TokenType.INT_LITERAL, "".join(lex), start_line, start_col)
        # Two‑character operators
        two = ch + self._peek(1)
        if two in {"==", "!=", "<=", ">=", "->"}:
            self._advance(); self._advance()
            mapping = {"==": TokenType.EQ, "!=": TokenType.NEQ, "<=": TokenType.LE, ">=": TokenType.GE, "->": TokenType.ARROW}
            return Token(mapping[two], two, start_line, start_col)
        # Single‑character tokens
        single_map = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "=": TokenType.ASSIGN,
            "<": TokenType.LT,
            ">": TokenType.GT,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ".": TokenType.DOT,
            "&": TokenType.AMP,
        }
        if ch in single_map:
            self._advance()
            return Token(single_map[ch], ch, start_line, start_col)
        raise LexerError(f"Unexpected character '{ch}'", start_line, start_col)
