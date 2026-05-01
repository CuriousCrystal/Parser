from src.lexer import Lexer, TokenType


def test_lexer_tokens_simple_declaration():
    source = "int x = 42;"
    lexer = Lexer(source)
    tokens = list(lexer.tokenize())

    assert tokens[0].type == TokenType.INT
    assert tokens[0].lexeme == "int"
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].lexeme == "x"
    assert tokens[2].type == TokenType.ASSIGN
    assert tokens[3].type == TokenType.INT_LITERAL
    assert tokens[3].lexeme == "42"
    assert tokens[4].type == TokenType.SEMICOLON
    assert tokens[5].type == TokenType.EOF


def test_lexer_skips_comments_and_whitespace():
    source = "int x; // comment\n/* block */ int y;"
    lexer = Lexer(source)
    tokens = [token.type for token in lexer.tokenize()]
    assert tokens == [
        TokenType.INT,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.INT,
        TokenType.IDENTIFIER,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ]
