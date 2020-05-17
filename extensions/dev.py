import io
import discord
import textwrap
import warnings
import contextlib
from discord.ext import commands
from typing import Any, Dict, List
from ftg.extensions.utils.context import Context


class EvalWarning(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


# noinspection PyBroadException
class DevCog(commands.Cog):
    """
    Cog for developer-related commands.
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: Context) -> None:
        await ctx.send(desc=f"You sure, {ctx.author}?")
        resp = await self.client.wait_for(
            "message", check=lambda msg: msg.author == ctx.author
        )
        if resp.content.startswith("y"):
            await ctx.send(desc="Alright. Shutting down...")
            await self.client.close()
        else:
            await ctx.send(desc="Alright then.")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: Context, ext_name: str) -> None:
        try:
            self.client.reload_extension(f"extensions.{ext_name}")
            await ctx.send(
                desc=f"Successfully reloaded the {ext_name} extension! \U0001f389"
            )
            await ctx.message.add_reaction("\U00002705")
        except Exception as e:
            await ctx.send(desc=str(e))

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx: Context, *, code: str) -> None:
        environment: Dict[str, Any] = {
            "commands": commands,
            "client": self.client,
            "discord": discord,
            "ctx": ctx,
        }
        environment.update(globals())
        std: io.StringIO = io.StringIO()

        if code.startswith("```") and code.endswith("```"):
            code = "\n".join(code.split("\n")[1:-1])

        compilation: str = f'async def _eval():\n{textwrap.indent(code, "    ")}'
        try:
            with warnings.catch_warnings(record=True) as w:
                exec(compilation, environment)
                if w:
                    raise EvalWarning(f"{w.__class__.__name__}: {str(w)}")
        except EvalWarning as e:
            await ctx.send(content=f"```\n{str(e)}\n```")
        except Exception as e1:
            await ctx.send(content=f"```\n{e1.__class__.__name__}: {(str(e1))}\n```")

        else:
            _eval: Any = environment["_eval"]
            try:
                with contextlib.redirect_stdout(std):
                    with warnings.catch_warnings(record=True) as w:
                        ret: Any = await _eval()
                        if "send" not in code:
                            await ctx.send(content=f"```\n{std.getvalue() or ret}\n```")
                        if w:
                            raise EvalWarning(
                                f"{w[0].category.__name__}: {w[0].message}"
                            )
            except EvalWarning as e0:
                await ctx.send(content=f"```\n{str(e0)}\n```")
            except Exception as e:
                await ctx.send(content=f"```\n{e.__class__.__name__}: {str(e)}\n```")


def setup(client: commands.Bot) -> None:
    client.add_cog(DevCog(client))
