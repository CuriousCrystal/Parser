from src.lexer import Lexer
from src.parser import Parser
from src.ast import (
    BreakStmt,
    CompoundStmt,
    ContinueStmt,
    ForStmt,
    FunctionDecl,
    Program,
    ReturnStmt,
    VarDecl,
    ExprStmt,
    IfStmt,
)


def test_parser_function_declaration():
    source = "int main() { return 0; }"
    parser = Parser(Lexer(source))
    program = parser.parse_program()

    assert isinstance(program, Program)
    assert len(program.declarations) == 1
    decl = program.declarations[0]
    assert isinstance(decl, FunctionDecl)
    assert decl.name == "main"
    assert decl.return_type.name == "int"
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


def test_parser_for_continue_break():
    source = """
    int main() {
        for (int i = 0; i < 3; i = i + 1) {
            if (i == 1) continue;
            break;
        }
        return 0;
    }
    """
    parser = Parser(Lexer(source))
    program = parser.parse_program()
    # Walk the AST to ensure a ForStmt with ContinueStmt and BreakStmt exists
    func = program.declarations[0]          # FunctionDecl for main
    assert isinstance(func, FunctionDecl)
    for_stmt = func.body.statements[0]   # first statement in the function body
    assert isinstance(for_stmt, ForStmt)
    # body of the for-loop should contain an IfStmt whose then-branch is ContinueStmt
    if_stmt = for_stmt.body.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert isinstance(if_stmt.then_branch, ContinueStmt)
    # second statement in the loop body should be BreakStmt
    assert isinstance(for_stmt.body.statements[1], BreakStmt)
    assert isinstance(func.body.statements[1], ReturnStmt)
