from src.lexer import Lexer
from src.parser import Parser
from src.ast import CompoundStmt, FunctionDecl, Program, ReturnStmt, VarDecl, ExprStmt


def test_parser_function_declaration():
    source = "int main() { return 0; }"
    parser = Parser(Lexer(source))
    program = parser.parse_program()

    assert isinstance(program, Program)
    assert len(program.declarations) == 1
    decl = program.declarations[0]
    assert isinstance(decl, FunctionDecl)
    assert decl.name == "main"
    assert decl.return_type == "int"
    assert isinstance(decl.body, CompoundStmt)
    assert isinstance(decl.body.statements[0], ReturnStmt)


def test_parser_variable_declaration_in_function():
    source = "int main() { int x = 10; x = x + 1; return x; }"
    parser = Parser(Lexer(source))
    program = parser.parse_program()

    assert isinstance(program.declarations[0], FunctionDecl)
    body = program.declarations[0].body
    assert len(body.statements) == 3
    assert isinstance(body.statements[0], VarDecl)
    assert isinstance(body.statements[1], ExprStmt)
    assert isinstance(body.statements[2], ReturnStmt)
