import pathlib

from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.codegen import CodeGenerator


def test_integration_compile_sample1():
    sample_path = pathlib.Path(__file__).parent.parent / "examples" / "sample1.c"
    source = sample_path.read_text(encoding="utf-8")
    program = Parser(Lexer(source)).parse_program()
    errors = SemanticAnalyzer().analyze(program)
    assert errors == []
    ir = CodeGenerator().generate(program)
    assert "FUNC main" in ir
    assert "RETURN" in ir
