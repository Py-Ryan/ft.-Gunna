import os
import json
import discord
import asyncpg
import asyncio
from discord.ext import commands
from traceback import extract_stack
from ftg.extensions.utils.context import Context
from typing import Any, Dict, List, Union, Optional


class Ftg(commands.Bot):

    def __init__(self, **options: Dict[str, Any]) -> None:
        super().__init__(command_prefix=self.get_prefix_, **options)
        self.app_info: Optional[discord.AppInfo] = None
        self.prefix_cache: Dict[int, str] = dict()
        self.__extensions__: List[str] = list()
        self.__url__: List[str] = list()

        with open("client/secret/secret.json") as secret:
            json.load(secret, object_hook=lambda d_: self.__url__.extend(
                [d_[key] for key in d_.keys() if key == 'url']
            ))

        self.db = asyncio.get_event_loop().run_until_complete(
            asyncpg.create_pool(self.__url__[0], min_size=1, max_size=5)
        )

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

    async def get_prefix_(self, bot: commands.Bot, message: discord.Message) -> Union[str, List[str]]:
        prefix: Optional[asyncpg.Record, str] = \
            await self.db.fetchrow("SELECT (prefix) FROM guilds WHERE id=$1", message.guild.id)
        if message.guild.id not in self.prefix_cache or self.prefix_cache[message.guild.id] != prefix:
            try:
                prefix = prefix["prefix"]
            except TypeError:
                prefix = "gn "
                await self.db.execute("INSERT INTO guilds (id, prefix) VALUES($1, $2)", message.guild.id, prefix)
            finally:
                self.prefix_cache[message.guild.id] = prefix

        return commands.when_mentioned_or(self.prefix_cache[message.guild.id])(bot, message)

    async def close(self) -> None:
        await self.db.close()
        await super().close()

    async def on_ready(self) -> None:
        print(f"READY payload on {self.user.name} - {self.user.id}")

        if not self.app_info:
            self.app_info = await self.application_info()

    async def on_message(self, message: discord.Message) -> None:
        if self.is_ready():
            ctx: Context = await self.get_context(message, cls=Context)
            await self.invoke(ctx)

    async def on_command_error(self, context: Context, exception: commands.CommandError) -> None:
        if not isinstance(exception, (commands.CommandNotFound, commands.CommandOnCooldown)):
            await context.send(desc=str(exception))
            await context.message.add_reaction("\U0000274c")
