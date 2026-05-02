"""Extended semantic analysis with support for arrays, pointers, and structs."""
from __future__ import annotations

from typing import Dict, List, Optional, Union

from .ast import (
    AddressOf,
    ArrayAccess,
    ArrayInit,
    ArrayType,
    BinaryOp,
    BreakStmt,
    CallExpr,
    CompoundStmt,
    ContinueStmt,
    Dereference,
    Expr,
    ExprStmt,
    ForStmt,
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
from .errors import SemanticError


class Symbol:
    def __init__(self, name: str, typ: Type | str, kind: str, params: Optional[List[Param]] = None):
        self.name = name
        self.type = typ
        self.kind = kind  # 'var', 'func', 'struct'
        self.params = params or []


class SemanticAnalyzer:
    def __init__(self):
        self.scopes: List[Dict[str, Symbol]] = [{}]
        self.struct_definitions: Dict[str, StructDecl] = {}
        self.errors: List[str] = []
        self.current_function_return: Optional[Type | str] = None

    def analyze(self, program: Program) -> List[str]:
        # First pass: collect struct definitions and function signatures
        for decl in program.declarations:
            if isinstance(decl, StructDecl):
                self._register_struct(decl)
            elif isinstance(decl, VarDecl):
                self._declare_variable(decl.name, self._normalize_type(decl.var_type))
                if decl.initializer:
                    self._expression_type(decl.initializer)
            elif isinstance(decl, FunctionDecl):
                return_type = self._normalize_type(decl.return_type)
                self._declare_function(decl.name, return_type, decl.params)
        
        # Second pass: analyze function bodies
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self._analyze_function(decl)
        
        return self.errors

    def _normalize_type(self, typ: Type | str) -> str | Type:
        """Convert type to string if it's a primitive, keep Type objects"""
        if isinstance(typ, str):
            return typ
        if isinstance(typ, PrimitiveType):
            return typ.name
        return typ

    def _register_struct(self, struct: StructDecl) -> None:
        """Register a struct definition"""
        self.struct_definitions[struct.name] = struct

    def _declare_variable(self, name: str, typ: Type | str) -> None:
        scope = self.scopes[-1]
        if name in scope:
            self.errors.append(f"Redeclaration of variable '{name}'")
            return
        scope[name] = Symbol(name=name, typ=typ, kind="var")

    def _declare_function(self, name: str, return_type: Type | str, params: List[Param]) -> None:
        global_scope = self.scopes[0]
        if name in global_scope:
            self.errors.append(f"Redeclaration of function '{name}'")
            return
        global_scope[name] = Symbol(
            name=name,
            typ=return_type,
            kind="func",
            params=params,
        )

    def _analyze_function(self, function: FunctionDecl) -> None:
        """Analyze a function's body"""
        self.scopes.append({})
        self.current_function_return = self._normalize_type(function.return_type)
        
        for param in function.params:
            param_type = self._normalize_type(param.param_type)
            self._declare_variable(param.name, param_type)
        
        self._visit_statement(function.body)
        self.scopes.pop()
        self.current_function_return = None

    def _visit_statement(self, stmt: Stmt, loop_depth: int = 0) -> None:
        if isinstance(stmt, CompoundStmt):
            self.scopes.append({})
            for item in stmt.statements:
                if isinstance(item, VarDecl):
                    item_type = self._normalize_type(item.var_type)
                    self._declare_variable(item.name, item_type)
                    if item.initializer:
                        self._expression_type(item.initializer)
                else:
                    self._visit_statement(item, loop_depth)
            self.scopes.pop()
            return
        
        if isinstance(stmt, VarDecl):
            item_type = self._normalize_type(stmt.var_type)
            self._declare_variable(stmt.name, item_type)
            if stmt.initializer:
                self._expression_type(stmt.initializer)
            return

        if isinstance(stmt, ExprStmt):
            self._expression_type(stmt.expr)
            return
        
        if isinstance(stmt, ReturnStmt):
            if stmt.value is None:
                return
            self._expression_type(stmt.value)
            return
        
        if isinstance(stmt, IfStmt):
            self._expression_type(stmt.condition)
            self._visit_statement(stmt.then_branch, loop_depth)
            if stmt.else_branch:
                self._visit_statement(stmt.else_branch, loop_depth)
            return
        
        if isinstance(stmt, WhileStmt):
            self._expression_type(stmt.condition)
            self._visit_statement(stmt.body, loop_depth + 1)
            return
        
        if isinstance(stmt, ForStmt):
            # Analyze init
            if stmt.init:
                self._visit_statement(stmt.init, loop_depth)
            # Condition
            if stmt.condition:
                self._expression_type(stmt.condition)
            # Update
            if stmt.update:
                self._expression_type(stmt.update)
            # Body
            self._visit_statement(stmt.body, loop_depth + 1)
            return
        
        if isinstance(stmt, ContinueStmt) or isinstance(stmt, BreakStmt):
            if loop_depth == 0:
                stmt_name = "continue" if isinstance(stmt, ContinueStmt) else "break"
                self.errors.append(f"'{stmt_name}' used outside of a loop")
            return

    def _lookup_symbol(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _expression_type(self, expr: Expr) -> Optional[Type | str]:
        if isinstance(expr, Literal):
            return "int"
        
        if isinstance(expr, Identifier):
            symbol = self._lookup_symbol(expr.name)
            if symbol is None:
                self.errors.append(f"Undefined identifier '{expr.name}'")
                return None
            return symbol.type
        
        if isinstance(expr, CallExpr):
            symbol = self._lookup_symbol(expr.callee.name)
            if symbol is None or symbol.kind != "func":
                self.errors.append(f"Call to undefined function '{expr.callee.name}'")
                return None
            
            expected = len(symbol.params)
            actual = len(expr.arguments)
            if expected != actual:
                self.errors.append(
                    f"Function '{expr.callee.name}' called with wrong number of arguments (expected {expected}, got {actual})"
                )
            
            for arg in expr.arguments:
                self._expression_type(arg)
            
            return symbol.type
        
        if isinstance(expr, ArrayAccess):
            array_type = self._expression_type(expr.array)
            self._expression_type(expr.index)
            
            if isinstance(array_type, ArrayType):
                return array_type.element_type
            elif isinstance(array_type, PointerType):
                return array_type.pointee
            else:
                self.errors.append(f"Subscript applied to non-array/non-pointer type")
                return None
        
        if isinstance(expr, Dereference):
            operand_type = self._expression_type(expr.operand)
            
            if isinstance(operand_type, PointerType):
                return operand_type.pointee
            else:
                self.errors.append(f"Dereference applied to non-pointer type")
                return None
        
        if isinstance(expr, AddressOf):
            operand_type = self._expression_type(expr.operand)
            if operand_type is None:
                return None
            return PointerType(pointee=operand_type)
        
        if isinstance(expr, MemberAccess):
            object_type = self._expression_type(expr.object)
            
            if isinstance(object_type, PointerType):
                object_type = object_type.pointee
            
            if isinstance(object_type, StructType) and object_type.members:
                for member_type, member_name in object_type.members:
                    if member_name == expr.member:
                        return member_type
                self.errors.append(f"Struct has no member '{expr.member}'")
                return None
            else:
                self.errors.append(f"Member access on non-struct type")
                return None
        
        if isinstance(expr, ArrayInit):
            element_types = []
            for elem in expr.elements:
                elem_type = self._expression_type(elem)
                if elem_type:
                    element_types.append(elem_type)
            if element_types:
                return ArrayType(element_type=element_types[0], size=len(element_types))
            return None
        
        if isinstance(expr, BinaryOp):
            left_type = self._expression_type(expr.left)
            right_type = self._expression_type(expr.right)
            
            if expr.operator == "=":
                if not isinstance(expr.left, Identifier):
                    self.errors.append("Left-hand side of assignment must be an lvalue")
                    return None
                return left_type
            
            if left_type is None or right_type is None:
                return None
            
            # Simple type compatibility
            if left_type == right_type:
                return left_type
            
            return left_type
        
        return None
