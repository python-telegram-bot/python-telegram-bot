import inspect
import re
from pathlib import Path

from telegram import Bot

ext_bot_path = Path(r"telegram\ext\_extbot.py")
bot_path = Path(r"telegram\_bot.py")
method_file = Path("new_method_bodies.py")
method_file.unlink(missing_ok=True)
bot_contents = bot_path.read_text(encoding="utf-8")
ext_bot_contents = ext_bot_path.read_text(encoding="utf-8")


def build_function(method_name: str, sig: inspect.Signature) -> str:
    params = ",".join(f"{param}={param}" for param in sig.parameters)
    params = params.replace(
        "api_kwargs=api_kwargs",
        "api_kwargs=self._merge_api_rl_kwargs(api_kwargs, rate_limit_args)",
    ).replace("self=self,", "")
    call = f"return await super().{method_name}({params})"
    match = re.search(
        rf"async def {re.escape(method_name)}\(([^\)]+)\)([^:]+):",
        bot_contents,
    )
    return f"async def {method_name}({match.group(1)}rate_limit_args: RL_ARGS=None){match.group(2)}:\n    {call}"


for name, method in inspect.getmembers(Bot, inspect.iscoroutinefunction):
    if name.startswith("_") or "_" not in name:
        continue
    if name.lower().replace("_", "") == "getupdates":
        continue
    if f"async def {name}" in ext_bot_contents:
        continue
    signature = inspect.signature(method, follow_wrapped=True)
    with method_file.open(mode="a") as file:
        file.write("\n\n" + build_function(name, signature))
