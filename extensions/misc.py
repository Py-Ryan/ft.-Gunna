from discord.ext import commands
from discord import User, Embed, Message
from ftg.extensions.utils.context import Context


class MiscCog(commands.Cog):
    """
    Cog for random, misc commands.
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def info(self, ctx: Context) -> None:
        owner: User = self.client.app_info.owner
        embed: Embed = Embed(title="Info", colour=ctx.__randcolor__())
        embed.add_field(
            name="Total Guild Count:", value=len(self.client.guilds), inline=True
        )
        embed.add_field(name="Total Member Count:", value=len(self.client.users))
        embed.description = "[Source Code](https://github.com/Py-Ryan/ft.-Gunna)"
        embed.set_footer(text=f"Bot Developer: {str(owner)} ({owner.id})")
        await ctx.send(embed=embed, reaction="\U00002705")

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.has_permissions(manage_guild=True)
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
            del self.client.prefix_cache[ctx.guild.id]
            await self.client.db.execute(
                """UPDATE guilds 
                                            SET prefix=$1 
                                            WHERE id=$2""",
                new_prefix,
                ctx.guild.id,
            )
            await ctx.send(desc="Alright, the new guild prefix is set.")
        else:
            await ctx.send(desc="Alright, I didn't change anything.")


def setup(client: commands.Bot) -> None:
    client.add_cog(MiscCog(client))
