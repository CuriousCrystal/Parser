"""AST node definitions for the C‑subset compiler.

Extended to support arrays, pointers, and structs.
Each node is a frozen ``@dataclass`` so that it is hashable and immutable.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Base classes
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Node:
    """Base class for all AST nodes – mainly for type checking convenience."""


@dataclass(frozen=True)
class Expr(Node):
    pass


@dataclass(frozen=True)
class Stmt(Node):
    pass


# ---------------------------------------------------------------------------
# Type system (for arrays, pointers, structs)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Type(Node, ABC):
    """Base class for all types."""


@dataclass(frozen=True)
class PrimitiveType(Type):
    """int, char, float, void."""
    name: str


@dataclass(frozen=True)
class PointerType(Type):
    """Pointer to another type (e.g., int*)."""
    pointee: Type


@dataclass(frozen=True)
class ArrayType(Type):
    """Array of another type (e.g., int[10])."""
    element_type: Type
    size: Optional[int] = None  # None means unsized array


@dataclass(frozen=True)
class StructType(Type):
    """Struct type with named members."""
    name: str
    members: Optional[List[tuple[Type, str]]] = None  # (type, name) pairs


# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Literal(Expr):
    value: int  # only integer literals for the subset


@dataclass(frozen=True)
class ArrayInit(Expr):
    """Array initializer: { 1, 2, 3 }"""
    elements: List[Expr]


@dataclass(frozen=True)
class Identifier(Expr):
    name: str


@dataclass(frozen=True)
class BinaryOp(Expr):
    left: Expr
    operator: str  # e.g. '+', '-', '*', '/', '==', '<', etc.
    right: Expr


@dataclass(frozen=True)
class CallExpr(Expr):
    callee: Identifier
    arguments: List[Expr]


@dataclass(frozen=True)
class ArrayAccess(Expr):
    array: Expr
    index: Expr


@dataclass(frozen=True)
class Dereference(Expr):
    operand: Expr


@dataclass(frozen=True)
class AddressOf(Expr):
    operand: Expr


@dataclass(frozen=True)
class MemberAccess(Expr):
    object: Expr
    member: str
    is_pointer: bool = False  # True for -> operator, False for . operator


# ---------------------------------------------------------------------------
# Statements
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ExprStmt(Stmt):
    expr: Expr


@dataclass(frozen=True)
class ReturnStmt(Stmt):
    value: Optional[Expr]


@dataclass(frozen=True)
class CompoundStmt(Stmt):
    statements: List[Stmt]


@dataclass(frozen=True)
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt] = None


@dataclass(frozen=True)
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt


# ---------------------------------------------------------------------------
# Declarations
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class VarDecl(Node):
    var_type: str | Type  # type name or Type object
    name: str
    initializer: Optional[Expr] = None


@dataclass(frozen=True)
class Param(Node):
    param_type: str | Type  # type name or Type object
    name: str


@dataclass(frozen=True)
class StructMember(Node):
    member_type: str | Type
    name: str


@dataclass(frozen=True)
class StructDecl(Node):
    """struct name { ... }"""
    name: str
    members: List[StructMember]


@dataclass(frozen=True)
class FunctionDecl(Node):
    return_type: str | Type
    name: str
    params: List[Param]
    body: CompoundStmt


@dataclass(frozen=True)
class Program(Node):
    declarations: List[Node]  # VarDecl, FunctionDecl, or StructDecl
