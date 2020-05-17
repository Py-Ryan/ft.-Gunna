from discord.ext import commands
from typing import Union, Optional
from ftg.extensions.utils.context import Context

from discord import (
    User,
    Embed,
    Member,
    Forbidden,
    HTTPException,
    Object as Snowflake,
)


class MemberCog(commands.Cog):
    """
    Cog for commands that interact with members and users.
    """

    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def kick(self, ctx: Context, members: commands.Greedy[Member], *, reason: str = "None") -> None:
        """
        Kick a member from your guild.

        You need the following permissions
        ----------------------------------
        `KICK_MEMBERS`

        Arguments
        ---------
        members:
            A member, or a spaced-list of members to kick.
        reason:
            The reason for the kick. Defaults to None.
        """
        embed: Embed = Embed(title="Kicked.", colour=ctx.__randcolor__())
        embed.add_field(
            name="Kicked By:", value=f"{ctx.author} ({ctx.author.id})", inline=True
        )
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)

        if members:
            curr_member: Optional[Member] = None
            try:
                for member in members:
                    curr_member = member
                    await ctx.guild.kick(
                        curr_member,
                        reason=f"Kicked By: {ctx.author}({ctx.author.id}) | Reason: {reason}",
                    )
            except HTTPException:
                await ctx.send(
                    desc=f"I couldn't kick {curr_member}.", reaction="\U0000274c"
                )
            else:
                await ctx.send(desc="They're gone \U0001f44c", reaction="\U00002705")
        else:
            raise commands.BadArgument("No user(s) were provided to kick.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def ban(self, ctx: Context, users: commands.Greedy[Union[Member, User, int]], *, rsn: str = "None") -> None:
        """
        Ban a member from your guild. Supports hackbanning if provided with an ID.

        You need the following permissions
        ----------------------------------
        `BAN_MEMBERS`

        Arguments
        ---------
        users:
            A user, or a spaced-list of users to ban. The user must be an ID to hackban.
            For a typical ban, the user can be a mention, or user#discrim, and ID.
        rsn:
            The reason for the ban. Defaults to None.
        """
        # Check if `users` is a list of Snowflake IDs, if so, change them all to Snowflakes.
        if isinstance(users, list):
            for user_ in range(len(users)):
                if isinstance(users[user_], int):
                    users[user_] = Snowflake(id=users[user_])
        elif isinstance(users, int):
            users = Snowflake(id=users)

        embed: Embed = Embed(title="Banned.", colour=ctx.__randcolor__())
        embed.add_field(
            name="Banned By:", value=f"{ctx.author} ({ctx.author.id})", inline=True
        )
        embed.add_field(name="Reason:", value=rsn, inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)

        curr_user: Optional[Union[Member, User, Snowflake, int]] = None
        try:
            for user_ in users:
                curr_user = user_
                await ctx.guild.ban(
                    curr_user,
                    reason=f"Banned by {ctx.author}({ctx.author.id}) | Reason: {rsn}",
                )
        except HTTPException:
            if isinstance(curr_user, Snowflake):
                curr_user = curr_user.id

            await ctx.send(
                desc=f"I couldn't ban {str(curr_user)}. Either they don't exist or they're more powerful than me.",
                reaction="\U0000274c",
            )
        else:
            # An attempt to find external shared guilds with a Snowflake in order to send them a ban notification.
            for user_ in users:
                if isinstance(user_, Snowflake):
                    try:
                        await self.client.get_user(user_.id).send(embed=embed)
                    except (AttributeError, Forbidden):
                        pass
                else:
                    try:
                        await user_.send(embed=embed)
                    except Forbidden:
                        pass

            await ctx.send(desc=f"They're gone \U0001f44c", reaction="\U00002705")


def setup(client: commands.Bot) -> None:
    client.add_cog(MemberCog(client))
