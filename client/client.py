import os
import json
import asyncpg
import aiohttp
import asyncio

from discord.ext import commands
from traceback import extract_stack
from ftg.extensions.utils.context import Context


class Ftg(commands.Bot):
    """Main bot class."""

    __slots__ = ("session", "deleted_message_cache", "cache", "_url", "app_info", "db")

    def __init__(self, **options):
        super().__init__(command_prefix=self.get_prefix_, **options)
        self.session = aiohttp.ClientSession()
        self.cache = {"prefix": {}, "messages": {}}
        self.app_info = None
        self._url = []

        with open("client/secret/secret.json") as secret:
            json.load(
                secret,
                object_hook=lambda d_: self._url.extend(
                    [d_[key] for key in d_.keys() if key == "url"]
                ),
            )

        self.db = asyncio.get_event_loop().run_until_complete(
            asyncpg.create_pool(self._url[0], min_size=1, max_size=5)
        )

    def run(self, token, extensions, **options):
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

        guild_entries = asyncio.get_event_loop().run_until_complete(
            self.db.fetch("""SELECT (id, prefix) FROM guilds""")
        )

        if guild_entries:
            for guild in guild_entries:
                guild = guild["row"]
                if guild[1]:
                    self.cache["prefix"][guild[0]] = guild[1]

        super().run(token, **options)

    async def get_prefix_(self, bot, message):
        if not self.cache["prefix"].get(message.guild.id):
            self.cache["prefix"][message.guild.id] = "gn "

        return commands.when_mentioned_or(self.cache["prefix"][message.guild.id])(bot, message)

    async def close(self):
        await self.db.close()
        await self.session.close()
        await super().close()

    async def on_ready(self):
        print(f"READY payload on {self.user.name} - {self.user.id}")

        if not self.app_info:
            self.app_info = await self.application_info()

    async def on_message(self, message):
        if self.is_ready():
            ctx = await self.get_context(message, cls=Context)
            await self.invoke(ctx)

    async def on_guild_remove(self, guild):
        if self.is_ready():
            await self.db.execute(
                """
                DELETE FROM guilds
                WHERE id=$1
                """,
                guild.id
            )

    async def on_command(self, ctx):
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

    async def on_command_error(self, ctx, exception):
        exception = getattr(exception, "original", exception)

        if not isinstance(exception, (commands.CommandNotFound, commands.CommandOnCooldown)):
            await ctx.send(desc=str(exception))
            await ctx.message.add_reaction(ctx.reactions.get("x"))
