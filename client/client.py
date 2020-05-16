import os
import discord
from discord.ext import commands
from typing import Any, Dict, List
from traceback import extract_stack
from ftg.extensions.utils.context import Context


class Ftg(commands.Bot):

    def __init__(self, **options: Dict[str, Any]) -> None:
        super().__init__(command_prefix="gn ", **options)
        self.__extensions__: List[str] = list()
        self.error_messages: Dict[str, str] = {
            "NotOwner": "",
            "CommandOnCooldown": "",
            "BadArgument": "Incorrect argument(s): {}",
            "BadUnionArgument": "I can't convert {} to {}"
        }

    def run(self, token: str, extensions: List[str], **options: Dict[str, Any]) -> None:
        if extensions:
            for ext in extensions:
                (root, ext) = os.path.splitext(ext)
                if ext == ".py":
                    self.__extensions__.append(f"extensions.{root}")

            for extension in self.__extensions__:
                self.load_extension(extension)
                print(f"Mounted extension: {extension[11:]}")

        elif not isinstance(extensions, list) or not extensions:
            class_name: str = self.__class__.__name__
            func_name: str = extract_stack(None, 2)[1][2]
            raise RuntimeWarning(f"No extensions were passed to {class_name}.{func_name}()")

        super().run(token, **options)

    async def on_ready(self) -> None:
        print(f"READY payload on {self.user.name} - {self.user.id}")
        await self.change_presence(activity=discord.Game(name='prefix: gn | https://github.com/Py-Ryan/ft.-Gunna'))

    async def on_message(self, message: discord.Message) -> None:
        ctx: Context = await self.get_context(message, cls=Context)
        await self.invoke(ctx)

    async def on_command_error(self, context: Context, exception: Any) -> None:
        error_msg: str = self.error_messages.get(exception.__class__.__name__, None)
        if error_msg:
            if '{}' in error_msg:
                error_msg = error_msg.format(*exception.param)
            await context.send(desc=error_msg)
        await context.message.add_reaction("\U0000274c")
