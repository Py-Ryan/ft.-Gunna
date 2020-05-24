import json

from discord.ext import commands
from discord import User, File, Embed, Message
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
        owner: User = self.client.get_user(self.client.owner_id)
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
    async def binify(self, ctx: Context, *, val: str) -> None:
        res = int("".join(format(ord(c), 'b') for c in val))

        embed = Embed(
            colour=ctx.__randcolor__(),
            title="Binary Conversion",
        )

        if len(str(res)) >= 2048:
            async with self.client.session.post('https://hastebin.com/documents', data=res) as s:
                h_code = json.loads(await s.text())["key"]
                await ctx.send(
                    title=f"https://hastebin.com/{h_code}",
                    desc=f"Your request was very long. So the binary is in a haste, {ctx.author.display_name}.",
                )
        elif 500 <= len(str(res)) < 2048:
            embed.description = \
                f"**Here is your converted text, {ctx.author.display_name}:**\n{res}"

            await ctx.send(
                desc=f"Long request, check your DMs, {ctx.author.display_name}.",
                reaction="\U00002705",
            )
            await ctx.author.send(embed=embed)
        else:
            embed.description = \
                f"**Here is your converted text, {ctx.author.display_name}:**\n{res}"

            await ctx.send(embed=embed, reaction="\U00002705")

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def unbinify(self, ctx: Context, *, binary: str) -> None:
        res = ""

        for i in range(0, len(binary), 7):
            td = binary[i:i+7]
            dd = int(td, 2)
            res += chr(dd)

        embed = Embed(
            colour=ctx.__randcolor__(),
            title="Binary Conversion",
        )

        res_len = len(res)
        if res_len <= 500:
            embed.description = \
                f"**Here is your converted text, {ctx.author.display_name}:**\n{res}"

            await ctx.send(
                embed=embed
            )
        elif 2048 >= res_len > 500:
            embed.description = \
                f"**Here is your converted text, {ctx.author.display_name}:**\n{res}"

            await ctx.send(
                desc="Long request, I'll send it in your DMs."
            )

            await ctx.author.send(embed=embed)
        else:
            async with self.client.session.post("https://hastebin.com/documents", data=res) as s:
                h_code = json.loads(await s.text())["key"]
                embed.title = f"https://hastebin.com/{h_code}"
                embed.description = "Very long request. I've uploaded it to hastebin, {ctx.author.display_name}"

            await ctx.send(desc=embed)


def setup(client: commands.Bot) -> None:
    client.add_cog(MiscCog(client))
