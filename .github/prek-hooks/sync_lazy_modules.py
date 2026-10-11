#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2026
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
"""Sync literal lazy-module lists with following top-level imports, without importing PTB."""

import ast
import json
from importlib.util import resolve_name
from pathlib import Path


def sync_lazy_modules(path: Path, package: str) -> bool:
    """Rewrite only the list; imports before its declaration stay eager."""
    source = path.read_bytes()
    tree = ast.parse(source, filename=str(path))
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "__lazy_modules__"
            for target in node.targets
        )
    )
    value = assignment.value
    if not isinstance(value, ast.List):
        message = f"Expected a literal __lazy_modules__ list in {path}"
        raise TypeError(message)

    modules: set[str] = set()
    for node in tree.body:
        if node.lineno <= assignment.lineno:
            continue
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and all(alias.name != "*" for alias in node.names):
            modules.add(resolve_name("." * node.level + (node.module or ""), package))

    # AST columns count UTF-8 bytes, so splice bytes rather than decoded characters.
    lines = source.splitlines(keepends=True)
    start = sum(map(len, lines[: value.lineno - 1])) + value.col_offset
    end = sum(map(len, lines[: (value.end_lineno or value.lineno) - 1])) + (
        value.end_col_offset or 0
    )
    newline = "\r\n" if b"\r\n" in source else "\n"
    entries = [f"    {json.dumps(module)}," for module in sorted(modules)]
    replacement = newline.join(["[", *entries, "]"]).encode("utf-8")
    updated = source[:start] + replacement + source[end:]
    if updated == source:
        return False
    path.write_bytes(updated)
    return True


def main() -> int:
    """Update both package initializers and signal pre-commit when files changed."""
    root = Path(__file__).resolve().parents[2]
    changed = False
    for package in ("telegram", "telegram.ext"):
        path = root / "src" / Path(*package.split(".")) / "__init__.py"
        if sync_lazy_modules(path, package):
            print(f"Updated {path.relative_to(root)}")  # noqa: T201
            changed = True
    return int(changed)


if __name__ == "__main__":
    raise SystemExit(main())
