# Examples

## Example 1

`examples/sample1.c` contains a simple `main` function that computes a small loop and returns a value.

## Example 2

`examples/sample2.c` contains a function call and local variable arithmetic.

## Running examples

```powershell
python -m src examples\sample1.c
python -m src examples\sample2.c
python -m src examples\for_demo.c
```

The output is a simple IR representation produced by `src/codegen.py`.

## Example 3

`examples/for_demo.c` demonstrates a `for` loop with `continue` and `break` inside a C-like function.
