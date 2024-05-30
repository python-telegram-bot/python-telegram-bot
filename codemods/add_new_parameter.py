#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].

import sys
from pathlib import Path

import libcst as cst
from libcst.display import dump

sys.path.insert(0, str(Path.cwd().absolute()))

from tests.test_official.scraper import TelegramParameter


class BotVisitor(cst.CSTVisitor):
    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        if node.name.value == "send_message":
            print("returning true for ", node.name.value)
            return True
        return False

    def visit_Arg(self, node: cst.Arg) -> None:
        print(node.value.value)


class BotTransformer(cst.CSTTransformer):
    def __init__(self, methods: dict[str, TelegramParameter]) -> None:
        self.methods = methods
        self.stack: list[tuple[str, ...]] = []

    def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
        self.stack.append((node.name.value,))
        return node.name.value in self.methods

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        method_name = self.stack.pop()
        if original_node.name.value not in self.methods:
            return original_node
        print(dump(updated_node))

        # get which method we are in
        method_name = method_name[0]
        tg_param = self.methods.pop(method_name)
        # Let's add our parameter now at the last position:

        # if the arg is required, we will add it to the end anyway (backward compat) and have a
        # type hint of Optional[<type>].
        annot = cst.Annotation(
            annotation=cst.Subscript(
                value=cst.Name(value="Optional"),
                slice=[
                    cst.SubscriptElement(
                        slice=cst.Index(value=cst.Name(value=tg_param.param_type))
                    )
                ],
            )
        )
        new_param = cst.Param(
            name=cst.Name(tg_param.param_name),
            annotation=annot,
            default=cst.Name(value="None"),
            comma=original_node.params.params[-1].comma,
            whitespace_after_param=original_node.params.params[-1].whitespace_after_param,
        )
        new_params = (*updated_node.params.params, new_param)
        return updated_node.with_changes(
            params=updated_node.params.with_changes(params=new_params)
        )


def add_param_to_bot_method(method_name: str, param: TelegramParameter) -> None:
    """Add a parameter to a method in the Bot class.

    Args:
        method_name (str): The name of the method.
        param (TelegramParameter): The parameter to add.
    """
    # All ast editing is done in place
    bot_file = Path("telegram/_bot.py")
    with bot_file.open() as file:
        source = cst.parse_module(file.read())
        # s = dump(source)
        mod_tree = source.visit(BotTransformer({method_name: param}))
        code = mod_tree.code

    with bot_file.open("w") as file:
        file.write(code)


if __name__ == "__main__":
    add_param_to_bot_method("send_message", TelegramParameter("effect_id", "str", False, "desc"))
    # failures = parse_failures()
    # missing_method_params = failures[0]
    # for method_name, param in missing_method_params.items():
    #     print("Adding parameter", param.param_name, "to method", method_name)
    #     add_param_to_bot_method(method_name, param)
    #     break
