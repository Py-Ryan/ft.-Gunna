import discord

from discord.ext import commands


class MiscCog(commands.Cog):

    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def info(self, ctx):
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

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def binaryout(self, ctx, *, text):
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
            async with self.client.session.post("https://hastebin.com/documents", data=result) as res:
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
    async def binaryin(self, ctx, *, text):
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
            async with self.client.session.post("https://hastebin.com/documents", data=result) as res:
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


def setup(client):
    client.add_cog(MiscCog(client))

