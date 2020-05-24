from discord import Message
from discord.ext import commands
from ftg.extensions.utils.context import Context


class GuildCog(commands.Cog):
    """
    Cog for guild-related commands.
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def leave(self, ctx: Context) -> None:
        """
        Make the bot leave the guild.

        Permissions Required
        --------------------
        `MANAGE_GUILD`
        """
        await ctx.send(desc=f"You sure you want me to leave, {ctx.author}?")
        confirmation: Message = await self.client.wait_for(
            "message", check=lambda msg: msg.author == ctx.author
        )
        if confirmation.content.startswith("y"):
            await ctx.send(desc="Alright, leaving. \U0001f44c", reaction="\U00002705")
            await ctx.guild.leave()
        else:
            await ctx.send(
                desc="Didn't get an answer starting with 'y'. Guess I'll stay. \U0001f44c"
            )

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.check(lambda x: x.author.id == 700091773695033505 or x.author.guild_permissions.manage_guild)
    async def prefix(self, ctx: Context, new_prefix: str) -> None:
        if new_prefix == "reset":
            new_prefix = "gn "
        await ctx.send(
            desc=f"Are you sure you wanna make the new guild prefix '{new_prefix}'"
        )
        response: Message = await self.client.wait_for(
            "message", check=lambda m: m.author == ctx.author
        )

        if response.content.startswith("y"):
            await self.client.db.execute(
                """
                INSERT INTO guilds(id, prefix)
                VALUES($1, $2)
                ON CONFLICT (id)
                DO UPDATE
                SET prefix=$2
                """,
                ctx.guild.id,
                new_prefix
            )
            self.client.__cache__["prefix"][ctx.guild.id] = new_prefix
            await ctx.send(desc="Alright, the new guild prefix is set.")
        else:
            await ctx.send(desc="Alright, I didn't change anything.")


def setup(client: commands.Bot) -> None:
    client.add_cog(GuildCog(client))
