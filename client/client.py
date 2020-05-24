import os
import json
import discord
import asyncpg
import aiohttp
import asyncio

from discord.ext import commands
from traceback import extract_stack
from typing import Any, Dict, List, Union
from ftg.extensions.utils.context import Context

import discord

from discord.ext import commands


class Ftg(commands.Bot):

    def __init__(self, **options: Dict[str, Any]) -> None:
        super().__init__(command_prefix=self.get_prefix_, **options)
        self.session = aiohttp.ClientSession()
        self.__cache__ = {"prefix": {}}
        self.__url__ = list()
        self.app_info = None

        with open("client/secret/secret.json") as secret:
            json.load(
                secret,
                object_hook=lambda d_: self.__url__.extend(
                    [d_[key] for key in d_.keys() if key == "url"]
                ),
            )

        self.db = asyncio.get_event_loop().run_until_complete(
            asyncpg.create_pool(self.__url__[0], min_size=1, max_size=5)
        )

    def run(self, token: str, extensions: List[str], **options: Dict[str, Any]) -> None:
        if extensions:
            for ext in extensions:
                (base, ext) = os.path.splitext(ext)
                if ext == ".py":
                    self.load_extension(f"extensions.{base}")
                    print(f"Mounted: {base}")

        elif not isinstance(extensions, list) or not extensions:
            class_name = self.__class__.__name__
            func_name = extract_stack(None, 2)[1][2]
            raise RuntimeWarning(
                f"No extensions were passed to {class_name}.{func_name}()"
            )

        guild_entries: List[asyncpg.Record] = asyncio.get_event_loop().run_until_complete(
            self.db.fetchrow("""SELECT (id, prefix) FROM guilds""")
        )

        if guild_entries:
            for guild in guild_entries:
                self.__cache__["prefix"][guild[0]] = guild[1]

        super().run(token, **options)

    async def get_prefix_(self, bot: commands.Bot, message: discord.Message) -> Union[str, List[str]]:
        if not self.__cache__["prefix"].get(message.guild.id):
            self.__cache__["prefix"][message.guild.id] = "gn "

        return commands.when_mentioned_or(self.__cache__["prefix"][message.guild.id])(bot, message)

    async def close(self) -> None:
        await self.db.close()
        await self.session.close()
        await super().close()

    async def on_ready(self) -> None:
        print(f"READY payload on {self.user.name} - {self.user.id}")

        if not self.app_info:
            self.app_info = await self.application_info()

    async def on_message(self, message: discord.Message) -> None:
        if self.is_ready():
            ctx: Context = await self.get_context(message, cls=Context)
            await self.invoke(ctx)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        if self.is_ready():
            await self.db.execute(
                """
                DELETE FROM guilds
                WHERE id=$1
                """,
                guild.id
            )

    async def on_command(self, ctx: Context) -> None:
        row = await self.db.fetchrow(
            """
            SELECT id
            FROM guilds
            WHERE id=$1
            """,
            ctx.guild.id
        )

        if not row:
            await self.db.execute(
                """
                INSERT INTO guilds (id)
                VALUES ($1)
                """,
                ctx.guild.id
            )

    async def on_command_error(self, context: Context, exception: commands.CommandError) -> None:
        exception = getattr(exception, "original", exception)
        if not isinstance(exception, (commands.CommandNotFound, commands.CommandOnCooldown)):
            await context.send(desc=str(exception))
            await context.message.add_reaction("\U0000274c")
            raise exception
