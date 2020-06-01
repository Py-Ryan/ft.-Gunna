from discord.ext import commands


class GuildCog(commands.Cog):
    """Extension designated for commands that interact with the guild."""

    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def leave(self, ctx):
        """Makes me leave the guild."""

        await ctx.send(desc=f"You sure you want me to leave, {ctx.author}?")
        confirmation = await self.client.wait_for("message", check=lambda msg: msg.author == ctx.author)

        if confirmation.content.startswith("y"):
            await ctx.send(desc=f"Alright, leaving. {ctx.reactions.get('ok')}", reaction=ctx.reactions.get("check"))
            await ctx.guild.leave()
        else:
            await ctx.send(desc=f"Didn't get an answer starting with 'y'. Guess I'll stay. {ctx.reactions.get('ok')}")

    @commands.command()
    @commands.cooldown(1, 2, commands.BucketType.guild)
    @commands.check(lambda x: x.author.id == 700091773695033505 or x.author.guild_permissions.manage_guild)
    async def prefix(self, ctx, new_prefix):
        """Edit the guild prefix."""

        await ctx.send(desc=f"Are you sure you wanna make the new guild prefix '{new_prefix}'")

        response = await self.client.wait_for("message", check=lambda m: m.author == ctx.author)

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

            self.client.cache["prefix"][ctx.guild.id] = new_prefix
            await ctx.send(desc="Alright, the new guild prefix is set.", reaction=ctx.reactions.get("check"))
        else:
            await ctx.send(desc="Alright, I didn't change anything.")


def setup(client):
    client.add_cog(GuildCog(client))
