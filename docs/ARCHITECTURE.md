# Architecture

The project is organized in a classic compiler pipeline.

- `src/lexer.py` - tokenizes C source text into a stream of tokens
- `src/ast.py` - defines the abstract syntax tree nodes
- `src/parser.py` - recursive-descent parser that builds the AST
- `src/semantic.py` - semantic analysis pass with symbol tables and type checks
- `src/codegen.py` - simple IR emitter for the validated AST
- `src/__main__.py` - CLI entry point

## Data flow

1. `Lexer` reads source and yields `Token` objects
2. `Parser` consumes tokens to build a `Program` AST
3. `SemanticAnalyzer` validates declarations, scopes, and types
4. `CodeGenerator` emits text-based intermediate code

## Compilation stages

- Lexing: whitespace and comments removed, keywords recognized, token positions recorded
- Parsing: top-level declarations, function bodies, and expressions parsed with precedence
- Semantic analysis: variable/function declarations tracked, undefined identifiers reported, return types checked
- Code generation: pseudo three-address instructions generated for each function
