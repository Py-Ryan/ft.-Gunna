from discord.ext import commands
from discord import Embed, AppInfo
from ftg.extensions.utils.context import Context


class MiscCog(commands.Cog):
    """
    Cog for random, misc commands.
    """
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.command()
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @commands.cooldown(1, per=2, type=commands.BucketType.guild)
    async def info(self, ctx: Context) -> None:
        owner: AppInfo = await self.client.application_info()
        embed: Embed = Embed(title="Info", colour=ctx.__randcolor__())
        embed.add_field(name="Total Guild Count:", value=len(self.client.guilds), inline=True)
        embed.add_field(name="Total Member Count:", value=len(self.client.users))
        embed.description = "[We're open source](https://github.com/Py-Ryan/ft.-Gunna)"
        embed.set_footer(text=f"Bot Developer: {str(owner.owner)} ({owner.owner.id})")
        await ctx.send(embed=embed, reaction="\U00002705")


def setup(client: commands.Bot) -> None:
    client.add_cog(MiscCog(client))
