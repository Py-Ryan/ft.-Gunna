import io
import discord
import warnings
import textwrap
import traceback
import contextlib

from discord.ext import commands


class EvalWarning(Exception):

    __slots__ = "message"

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


# noinspection PyBroadException
class DevCog(commands.Cog):

    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send(desc=f"You sure, {ctx.author}?")
        resp = await self.client.wait_for("message", check=lambda msg: msg.author == ctx.author)

        if resp.content.startswith("y"):
            await ctx.send(desc="Alright. Shutting down...", reaction=ctx.reactions.get("check"))
            await self.client.close()
        else:
            await ctx.send(desc="Alright then.")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, ext_name):
        try:
            self.client.reload_extension(f"extensions.{ext_name}")
            await ctx.send(desc=f"Successfully reloaded the {ext_name} extension! \U0001f389")
            await ctx.message.add_reaction(ctx.reactions.get("check"))
        except Exception as e:
            raise RuntimeError(str(e))

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        environment = {
            "commands": commands,
            "client": self.client,
            "discord": discord,
            "ctx": ctx,
        }
        std = io.StringIO()

        environment.update(globals())
        environment.update(locals())

        if code.startswith("```") and code.endswith("```"):
            code = "\n".join(code.split("\n")[1:-1])

        compilation = \
f"""
async def _eval():
    ret = None
    try:
        with contextlib.redirect_stdout(std) as std_:
{textwrap.indent(code, '            ')}
{textwrap.indent("ret = std_", '            ')}
    finally:
        environment.update(locals())
    
    return ret
"""

        result = None

        try:
            exec(compilation, environment)
            with warnings.catch_warnings(record=True) as warning:
                result = await environment['_eval']()

                if warning:
                    raise EvalWarning(str(warning[0].message))
                else:
                    await ctx.message.add_reaction(ctx.reactions.get("check"))

        except EvalWarning as e:
            await ctx.send(desc=f'```\n{e}```')
            await ctx.message.add_reaction(ctx.reactions.get("x"))

        except Exception:
            result = traceback.format_exc()
            result = "\n".join(result.split("\n")[4:])
            await ctx.message.add_reaction(ctx.reactions.get("x"))

        finally:
            try:
                result = result.getvalue()
            except AttributeError:
                pass

            if "send" not in code:
                await ctx.send(desc=f"{f'```{result}```' if result else '```None```'}")


def setup(client):
    client.add_cog(DevCog(client))
