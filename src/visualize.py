from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any, Iterable

from .ast import Node, Program


def _format_label(label: str) -> str:
    escaped = label.replace('"', '\\"')
    return f'"{escaped}"'


def _is_sequence(value: Any) -> bool:
    return isinstance(value, list) or isinstance(value, tuple)


class _NodeRenderer:
    def __init__(self) -> None:
        self.lines: list[str] = ["flowchart TD"]
        self.count = 0

    def _new_id(self) -> str:
        node_id = f"n{self.count}"
        self.count += 1
        return node_id

    def render(self, root: Program) -> str:
        self._render_node(root)
        return "\n".join(self.lines)

    def _render_node(self, node: Any) -> str:
        if node is None:
            node_id = self._new_id()
            self.lines.append(f"{node_id}[\"None\"]")
            return node_id

        if isinstance(node, str):
            node_id = self._new_id()
            self.lines.append(f"{node_id}[{_format_label(node)}]")
            return node_id

        if isinstance(node, (int, float, bool)):
            node_id = self._new_id()
            self.lines.append(f"{node_id}[{_format_label(str(node))}]")
            return node_id

        if _is_sequence(node):
            node_id = self._new_id()
            self.lines.append(f"{node_id}[{_format_label('List')}]")
            for item in node:
                child_id = self._render_node(item)
                self.lines.append(f"{node_id} --> {child_id}")
            return node_id

        if is_dataclass(node) and isinstance(node, Node):
            node_id = self._new_id()
            label = type(node).__name__
            if hasattr(node, "name"):
                name = getattr(node, "name")
                if isinstance(name, str):
                    label = f"{label}({name})"
            self.lines.append(f"{node_id}[{_format_label(label)}]")
            for field in fields(node):
                value = getattr(node, field.name)
                if value is None:
                    continue
                child_id = self._render_node(value)
                self.lines.append(f"{node_id} --> {child_id}")
            return node_id

        node_id = self._new_id()
        self.lines.append(f"{node_id}[{_format_label(str(node))}]")
        return node_id


def ast_to_mermaid(program: Program) -> str:
    renderer = _NodeRenderer()
    return renderer.render(program)
