"""Extended code generation supporting arrays, pointers, and structs."""
from __future__ import annotations

from typing import List

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
    Literal,
    MemberAccess,
    PointerType,
    Program,
    ReturnStmt,
    Stmt,
    StructDecl,
    StructType,
    VarDecl,
    WhileStmt,
)
from .errors import CodeGenerationError


class CodeGenerator:
    def __init__(self):
        self.instructions: List[str] = []
        self.temp_count = 0
        self.label_count = 0

    def generate(self, program: Program) -> str:
        self.instructions.clear()
        self.temp_count = 0
        self.label_count = 0
        
        # Register struct definitions
        for decl in program.declarations:
            if isinstance(decl, StructDecl):
                self._emit(f"; struct {decl.name}")
        
        # Generate code for functions and globals
        for decl in program.declarations:
            if isinstance(decl, FunctionDecl):
                self._generate_function(decl)
            elif isinstance(decl, VarDecl):
                self._emit(f"GLOBAL {self._type_string(decl.var_type)} {decl.name}")
        
        return "\n".join(self.instructions)

    def _type_string(self, typ) -> str:
        """Convert type object to string"""
        if isinstance(typ, str):
            return typ
        if hasattr(typ, 'name'):
            return typ.name
        return "int"

    def _new_temp(self) -> str:
        name = f"t{self.temp_count}"
        self.temp_count += 1
        return name

    def _new_label(self) -> str:
        name = f"L{self.label_count}"
        self.label_count += 1
        return name

    def _emit(self, line: str) -> None:
        self.instructions.append(line)

    def _generate_function(self, func: FunctionDecl) -> None:
        self._emit(f"FUNC {func.name}")
        for param in func.params:
            param_type = self._type_string(param.param_type)
            self._emit(f"PARAM {param_type} {param.name}")
        self._generate_statement(func.body)
        self._emit(f"END_FUNC {func.name}")

    def _generate_statement(self, stmt: Stmt) -> None:
        if isinstance(stmt, CompoundStmt):
            for item in stmt.statements:
                self._generate_statement(item)
            return
        
        if isinstance(stmt, ExprStmt):
            self._generate_expression(stmt.expr)
            return
        
        if isinstance(stmt, ReturnStmt):
            return_value = "" if stmt.value is None else self._generate_expression(stmt.value)
            self._emit(f"RETURN {return_value}".strip())
            return
        
        if isinstance(stmt, WhileStmt):
            label_start = self._new_label()
            label_end = self._new_label()
            self._emit(f"LABEL {label_start}")
            cond = self._generate_expression(stmt.condition)
            self._emit(f"JUMP_IF_FALSE {cond} {label_end}")
            self._generate_statement(stmt.body)
            self._emit(f"JUMP {label_start}")
            self._emit(f"LABEL {label_end}")
            return
        
        if isinstance(stmt, VarDecl):
            var_type = self._type_string(stmt.var_type)
            self._emit(f"LOCAL {var_type} {stmt.name}")
            if stmt.initializer:
                value = self._generate_expression(stmt.initializer)
                self._emit(f"STORE {stmt.name} {value}")
            return

    def _generate_expression(self, expr: Expr) -> str:
        if isinstance(expr, Literal):
            return str(expr.value)
        
        if isinstance(expr, Identifier):
            return expr.name
        
        if isinstance(expr, CallExpr):
            args = [self._generate_expression(arg) for arg in expr.arguments]
            temp = self._new_temp()
            self._emit(f"CALL {temp} {expr.callee.name} {' '.join(args)}")
            return temp
        
        if isinstance(expr, ArrayAccess):
            array = self._generate_expression(expr.array)
            index = self._generate_expression(expr.index)
            temp = self._new_temp()
            self._emit(f"LOAD_ARRAY {temp} {array} {index}")
            return temp
        
        if isinstance(expr, Dereference):
            operand = self._generate_expression(expr.operand)
            temp = self._new_temp()
            self._emit(f"DEREF {temp} {operand}")
            return temp
        
        if isinstance(expr, AddressOf):
            operand = self._generate_expression(expr.operand)
            temp = self._new_temp()
            self._emit(f"ADDRESS {temp} {operand}")
            return temp
        
        if isinstance(expr, MemberAccess):
            obj = self._generate_expression(expr.object)
            if expr.is_pointer:
                self._emit(f"; pointer member access {obj}->{expr.member}")
            else:
                self._emit(f"; member access {obj}.{expr.member}")
            temp = self._new_temp()
            self._emit(f"MEMBER {temp} {obj} {expr.member}")
            return temp
        
        if isinstance(expr, ArrayInit):
            temp = self._new_temp()
            elements = [self._generate_expression(elem) for elem in expr.elements]
            self._emit(f"ARRAY_INIT {temp} {len(elements)} {' '.join(elements)}")
            return temp
        
        if isinstance(expr, BinaryOp):
            left = self._generate_expression(expr.left)
            right = self._generate_expression(expr.right)
            temp = self._new_temp()
            self._emit(f"{expr.operator} {temp} {left} {right}")
            return temp
        
        raise CodeGenerationError(f"Unsupported expression: {type(expr).__name__}")
