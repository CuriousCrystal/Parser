"""Extended recursive-descent parser for C with arrays, pointers, and structs."""
from __future__ import annotations

from typing import Iterator, List, Optional

from .ast import (
    AddressOf,
    ArrayAccess,
    ArrayInit,
    ArrayType,
    BinaryOp,
    CallExpr,
    CompoundStmt,
    Dereference,
    Expr,
    ExprStmt,
    FunctionDecl,
    Identifier,
    IfStmt,
    Literal,
    MemberAccess,
    Param,
    PointerType,
    PrimitiveType,
    Program,
    ReturnStmt,
    Stmt,
    StructDecl,
    StructMember,
    StructType,
    Type,
    VarDecl,
    WhileStmt,
)
from .errors import ParserError
from .lexer import Lexer, Token, TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self.tokens: Iterator[Token] = lexer.tokenize()
        self.current: Token = next(self.tokens)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _advance(self) -> Token:
        previous = self.current
        try:
            self.current = next(self.tokens)
        except StopIteration:
            self.current = Token(TokenType.EOF, "", previous.line, previous.column)
        return previous

    def _expect(self, typ: TokenType) -> Token:
        if self.current.type == typ:
            return self._advance()
        raise ParseError(f"Expected {typ.name}, found {self.current.type.name}", self.current)

    def _match(self, *types: TokenType) -> bool:
        if self.current.type in types:
            self._advance()
            return True
        return False

    def _peek(self, *types: TokenType) -> bool:
        return self.current.type in types

    def _is_type_specifier(self) -> bool:
        return self.current.type in {
            TokenType.INT,
            TokenType.CHAR,
            TokenType.FLOAT,
            TokenType.VOID,
            TokenType.STRUCT,
        }

    # ------------------------------------------------------------------
    # entry point
    # ------------------------------------------------------------------
    def parse_program(self) -> Program:
        declarations: List = []
        while self.current.type != TokenType.EOF:
            if self.current.type == TokenType.STRUCT:
                declarations.append(self._parse_struct_declaration())
            elif self._is_type_specifier():
                declarations.append(self._parse_declaration())
            else:
                raise ParseError("Unexpected token at top level", self.current)
        return Program(declarations)

    # ------------------------------------------------------------------
    # type parsing (int*, int[10], struct S, etc.)
    # ------------------------------------------------------------------
    def _parse_type(self) -> Type:
        """Parse a base type (int, char, struct S, etc.)"""
        if self.current.type == TokenType.STRUCT:
            self._advance()
            name = self._expect(TokenType.IDENTIFIER).lexeme
            return StructType(name=name, members=None)
        
        if self.current.type in {TokenType.INT, TokenType.CHAR, TokenType.FLOAT, TokenType.VOID}:
            typ = self._advance().lexeme
            return PrimitiveType(name=typ)
        
        raise ParseError("Expected type specifier", self.current)

    def _parse_declarator(self, base_type: Type) -> tuple[Type, str]:
        """Parse declarator with * and [] modifiers (e.g., *ptr, arr[10])"""
        # Handle leading * (pointers)
        while self._match(TokenType.STAR):
            base_type = PointerType(pointee=base_type)
        
        # Get the identifier name
        if not self._peek(TokenType.IDENTIFIER):
            raise ParseError("Expected identifier in declarator", self.current)
        name = self._advance().lexeme
        
        # Handle trailing [] (arrays)
        while self._match(TokenType.LBRACKET):
            size = None
            if self.current.type != TokenType.RBRACKET:
                if self.current.type == TokenType.INT_LITERAL:
                    size = int(self._advance().lexeme)
                else:
                    raise ParseError("Expected array size or ]", self.current)
            self._expect(TokenType.RBRACKET)
            base_type = ArrayType(element_type=base_type, size=size)
        
        return base_type, name

    # ------------------------------------------------------------------
    # declarations
    # ------------------------------------------------------------------
    def _parse_struct_declaration(self) -> StructDecl:
        """Parse struct definition: struct name { ... }"""
        self._expect(TokenType.STRUCT)
        name = self._expect(TokenType.IDENTIFIER).lexeme
        self._expect(TokenType.LBRACE)
        
        members: List[StructMember] = []
        while self.current.type != TokenType.RBRACE:
            if not self._is_type_specifier():
                raise ParseError("Expected type in struct", self.current)
            
            member_type = self._parse_type()
            member_decl_type, member_name = self._parse_declarator(member_type)
            members.append(StructMember(member_type=member_decl_type, name=member_name))
            self._expect(TokenType.SEMICOLON)
        
        self._expect(TokenType.RBRACE)
        self._expect(TokenType.SEMICOLON)
        return StructDecl(name=name, members=members)

    def _parse_declaration(self) -> VarDecl | FunctionDecl:
        """Parse variable or function declaration"""
        base_type = self._parse_type()
        decl_type, identifier = self._parse_declarator(base_type)
        
        if self._match(TokenType.LPAREN):
            # Function declaration
            params = self._parse_parameter_list()
            self._expect(TokenType.RPAREN)
            self._expect(TokenType.LBRACE)
            body = self._parse_compound_statement()
            return FunctionDecl(return_type=base_type, name=identifier, params=params, body=body)
        
        # Variable declaration
        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()
        self._expect(TokenType.SEMICOLON)
        return VarDecl(var_type=decl_type, name=identifier, initializer=initializer)

    def _parse_parameter_list(self) -> List[Param]:
        """Parse function parameter list"""
        params: List[Param] = []
        if self.current.type == TokenType.RPAREN:
            return params
        
        while True:
            if not self._is_type_specifier():
                raise ParseError("Expected type in parameter list", self.current)
            
            param_type = self._parse_type()
            param_decl_type, param_name = self._parse_declarator(param_type)
            params.append(Param(param_type=param_decl_type, name=param_name))
            
            if not self._match(TokenType.COMMA):
                break
        
        return params

    # ------------------------------------------------------------------
    # statements
    # ------------------------------------------------------------------
    def _parse_statement(self) -> Stmt:
        if self._match(TokenType.LBRACE):
            return self._parse_compound_statement()
        if self._match(TokenType.RETURN):
            value = None
            if self.current.type != TokenType.SEMICOLON:
                value = self._parse_expression()
            self._expect(TokenType.SEMICOLON)
            return ReturnStmt(value=value)
        if self._match(TokenType.IF):
            self._expect(TokenType.LPAREN)
            condition = self._parse_expression()
            self._expect(TokenType.RPAREN)
            then_branch = self._parse_statement()
            else_branch = None
            if self._match(TokenType.ELSE):
                else_branch = self._parse_statement()
            return IfStmt(condition=condition, then_branch=then_branch, else_branch=else_branch)
        if self._match(TokenType.WHILE):
            self._expect(TokenType.LPAREN)
            condition = self._parse_expression()
            self._expect(TokenType.RPAREN)
            body = self._parse_statement()
            return WhileStmt(condition=condition, body=body)
        if self._is_type_specifier():
            decl = self._parse_declaration()
            return decl
        
        expression = self._parse_expression()
        self._expect(TokenType.SEMICOLON)
        return ExprStmt(expression)

    def _parse_compound_statement(self) -> CompoundStmt:
        """Parse { ... }"""
        statements: List[Stmt] = []
        while self.current.type != TokenType.RBRACE:
            if self.current.type == TokenType.EOF:
                raise ParseError("Unterminated compound statement", self.current)
            statements.append(self._parse_statement())
        self._expect(TokenType.RBRACE)
        return CompoundStmt(statements=statements)

    # ------------------------------------------------------------------
    # expressions with postfix/unary operators
    # ------------------------------------------------------------------
    def _parse_expression(self) -> Expr:
        return self._parse_assignment()

    def _parse_assignment(self) -> Expr:
        expr = self._parse_equality()
        if self._match(TokenType.ASSIGN):
            if not isinstance(expr, Identifier):
                raise ParseError("Left-hand side of assignment must be an lvalue", self.current)
            value = self._parse_assignment()
            return BinaryOp(left=expr, operator="=", right=value)
        return expr

    def _parse_equality(self) -> Expr:
        expr = self._parse_relational()
        while self.current.type in {TokenType.EQ, TokenType.NEQ}:
            operator = self.current.lexeme
            self._advance()
            right = self._parse_relational()
            expr = BinaryOp(left=expr, operator=operator, right=right)
        return expr

    def _parse_relational(self) -> Expr:
        expr = self._parse_additive()
        while self.current.type in {TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE}:
            operator = self.current.lexeme
            self._advance()
            right = self._parse_additive()
            expr = BinaryOp(left=expr, operator=operator, right=right)
        return expr

    def _parse_additive(self) -> Expr:
        expr = self._parse_term()
        while self.current.type in {TokenType.PLUS, TokenType.MINUS}:
            operator = self.current.lexeme
            self._advance()
            right = self._parse_term()
            expr = BinaryOp(left=expr, operator=operator, right=right)
        return expr

    def _parse_term(self) -> Expr:
        expr = self._parse_unary()
        while self.current.type in {TokenType.STAR, TokenType.SLASH, TokenType.PERCENT}:
            operator = self.current.lexeme
            self._advance()
            right = self._parse_unary()
            expr = BinaryOp(left=expr, operator=operator, right=right)
        return expr

    def _parse_unary(self) -> Expr:
        """Unary operators: & (address-of), * (dereference)"""
        if self._match(TokenType.AMP):
            operand = self._parse_unary()
            return AddressOf(operand=operand)
        if self._match(TokenType.STAR):
            operand = self._parse_unary()
            return Dereference(operand=operand)
        return self._parse_postfix()

    def _parse_postfix(self) -> Expr:
        """Postfix operators: [], ., ->"""
        expr = self._parse_primary()
        
        while True:
            if self._match(TokenType.LBRACKET):
                # Array access: arr[index]
                index = self._parse_expression()
                self._expect(TokenType.RBRACKET)
                expr = ArrayAccess(array=expr, index=index)
            elif self._match(TokenType.DOT):
                # Member access: obj.field
                member = self._expect(TokenType.IDENTIFIER).lexeme
                expr = MemberAccess(object=expr, member=member, is_pointer=False)
            elif self._match(TokenType.ARROW):
                # Pointer member access: ptr->field
                member = self._expect(TokenType.IDENTIFIER).lexeme
                expr = MemberAccess(object=expr, member=member, is_pointer=True)
            elif self._match(TokenType.LPAREN) and isinstance(expr, Identifier):
                # Function call
                arguments = self._parse_argument_list()
                self._expect(TokenType.RPAREN)
                expr = CallExpr(callee=expr, arguments=arguments)
            else:
                break
        
        return expr

    def _parse_primary(self) -> Expr:
        """Primary expressions: literals, identifiers, parenthesized expressions"""
        if self.current.type == TokenType.INT_LITERAL:
            value = int(self.current.lexeme)
            self._advance()
            return Literal(value=value)
        
        if self.current.type == TokenType.IDENTIFIER:
            name = self.current.lexeme
            self._advance()
            return Identifier(name=name)
        
        if self._match(TokenType.LPAREN):
            # Could be grouped expression or array init
            if self.current.type == TokenType.RBRACE:
                # Empty group (shouldn't happen) 
                self._advance()
                return Literal(value=0)
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr
        
        if self._match(TokenType.LBRACE):
            # Array initializer: { 1, 2, 3 }
            elements: List[Expr] = []
            while self.current.type != TokenType.RBRACE:
                elements.append(self._parse_expression())
                if not self._match(TokenType.COMMA):
                    break
            self._expect(TokenType.RBRACE)
            return ArrayInit(elements=elements)
        
        raise ParseError("Expected expression", self.current)

    def _parse_argument_list(self) -> List[Expr]:
        """Parse function call arguments"""
        args: List[Expr] = []
        if self.current.type == TokenType.RPAREN:
            return args
        
        while True:
            args.append(self._parse_expression())
            if not self._match(TokenType.COMMA):
                break
        
        return args
