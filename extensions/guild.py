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


def setup(client: commands.Bot) -> None:
    client.add_cog(GuildCog(client))
