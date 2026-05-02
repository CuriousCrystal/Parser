The ParserLexer repository implements a simple compiler front‑end for a custom language. It contains a full lexical analyzer (lexer), a recursive‑descent parser, and semantic analysis modules, along with code‑generation back‑ends that emit an intermediate representation (IR). The source tree is organized as follows:

src – core implementation:
lexer.py tokenizes input source files.
parser.py builds an abstract syntax tree (AST) using the grammar described in GRAMMAR.md.
semantic.py performs type checking and scope resolution, while the extended versions (parser_extended.py, semantic_extended.py) add extra language features.
codegen.py and codegen_extended.py translate the AST into IR files stored under expected_output/.
ast.py defines the data structures for the AST nodes.
examples – sample source programs (sample1.c, sample2.c, for_demo.c) and their expected IR output for testing.
tests – a pytest suite (test_lexer.py, test_parser.py, test_integration.py) that validates each compilation stage.
docs – documentation covering the architecture, usage examples, and the language grammar.

Overall, the project demonstrates the classic compiler pipeline—lexical analysis, parsing, semantic analysis, and code generation—implemented in Python, making it a useful educational reference for building language tools. The language subset now includes C-like control structures such as `for` loops, `continue`, and `break`, with example programs and generated IR output provided for testing.
