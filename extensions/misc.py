import discord

from discord.ext import commands


class MiscCog(commands.Cog):
    """Extension designated to hold random methods - or methods with no dedicated cog yet."""

    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def info(self, ctx):
        """Generic bot information."""

        owner = self.client.get_user(self.client.owner_id)

        embed = discord.Embed(
            title="Info",
            colour=ctx.__randcolor__(),
            description="[Source Code](https://github.com/Py-Ryan/ft.-Gunna)"
        )
        embed.add_field(name="Total Guild Count:", value=len(self.client.guilds), inline=True)
        embed.add_field(name="Total Member Count:", value=len(self.client.users))
        embed.set_footer(text=f"Bot Developer: {str(owner)} ({owner.id})")

        await ctx.send(embed=embed, reaction=ctx.reactions.get("check"))

    async def hastebin_helper(self, ctx, data, embed):
        """Helper method designated for binaryout and binaryin."""

        async with self.client.session.post("https://hastebin.com/documents", data=data) as res:
            data = await res.json()

            try:
                message = data["key"]
                embed.add_field(
                    name="Hastebin Link:",
                    value=f"https://hastebin.com/{message}",
                    inline=True
                ).colour = ctx.__randcolor__()
                embed.description = None

                await ctx.send(embed=embed, reaction=ctx.reactions.get("check"))
            except KeyError:
                message = data["message"]
                embed.title = "Failed to POST on hastebin."
                embed.description = message

                await ctx.send(embed=embed, reaction=ctx.reactions.get("x"))

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def binaryout(self, ctx, *, text):
        """Convert inputted text into binary code."""

        result = " ".join([bin(ord(char))[2:].zfill(8) for char in text])

        embed = discord.Embed(
            colour=ctx.__randcolor__(),
            title="Binary Conversion",
            description=result,
        ).set_footer(icon_url=ctx.author.avatar_url_as(static_format='png'), text=f"Requested by {ctx.author}")

        length = len(result)

        if length <= 500:
            await ctx.send(embed=embed, reaction=ctx.reactions.get("check"))
        else:
            await type(self).hastebin_helper(self, ctx, result, embed)

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def binaryin(self, ctx, *, text):
        """Convert inputted binary code into text."""

        result = ''.join([chr(int(byte, 2)) for byte in text.split()])

        embed = discord.Embed(
            colour=ctx.__randcolor__(),
            title="Binary Conversion",
            description=result,
        ).set_footer(icon_url=ctx.author.avatar_url_as(static_format='png'), text=f"Requested by {ctx.author}")

        length = len(result)

        if length <= 500:
            await ctx.send(embed=embed, reaction=ctx.reactions.get("check"))
        else:
            await type(self).hastebin_helper(self, ctx, result, embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def snipe(self, ctx):
        """Snipe the most recently deleted message from your guild."""

        embed = discord.Embed(colour=ctx.__randcolor__())
        embed.set_footer(icon_url=ctx.author.avatar_url_as(static_format="png"), text=f"Requested by {ctx.author}")

        guild = self.client.cache["messages"].get(str(ctx.guild.id))

        if guild:
            entry = guild[0]
            embed.title = str(self.client.get_user(entry.author))
            embed.description = f"```{entry.content}```"
            await ctx.send(embed=embed)
        else:
            raise commands.CommandError("No message(s) to snipe.")


def setup(client):
    client.add_cog(MiscCog(client))

