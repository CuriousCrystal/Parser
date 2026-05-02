from src.lexer import Lexer
from src.parser import Parser
from src.visualize import ast_to_mermaid


def test_ast_visualization_generates_mermaid():
    source = "int main() { return 0; }"
    program = Parser(Lexer(source)).parse_program()
    diagram = ast_to_mermaid(program)

    assert diagram.startswith("flowchart TD")
    assert "FunctionDecl(main)" in diagram
    assert "ReturnStmt" in diagram
