# Grammar for the C Subset

This grammar defines the minimal subset supported by the compiler.

```
program          ::= declaration*

declaration      ::= type_specifier IDENTIFIER (function_declaration | variable_declaration)
function_declaration ::= '(' parameter_list ')' compound_statement
variable_declaration ::= ('=' expression)? ';'

parameter_list   ::= /* empty */ | parameter (',' parameter)*
parameter        ::= type_specifier IDENTIFIER

type_specifier   ::= 'int' | 'char' | 'float' | 'void'

statement        ::= compound_statement
                   | if_statement
                   | while_statement
                   | return_statement
                   | declaration
                   | expression_statement

compound_statement ::= '{' (declaration | statement)* '}'
if_statement     ::= 'if' '(' expression ')' statement ('else' statement)?
while_statement  ::= 'while' '(' expression ')' statement
return_statement ::= 'return' expression? ';'
expression_statement ::= expression ';'

expression       ::= assignment
assignment       ::= equality ('=' assignment)?
equality         ::= relational (('==' | '!=') relational)*
relational       ::= additive (('<' | '>' | '<=' | '>=') additive)*
additive         ::= term (('+' | '-') term)*
term             ::= factor (('*' | '/' | '%') factor)*
factor           ::= INT_LITERAL | IDENTIFIER | call_expression | '(' expression ')'
call_expression  ::= IDENTIFIER '(' argument_list ')'
argument_list    ::= /* empty */ | expression (',' expression)*
```
