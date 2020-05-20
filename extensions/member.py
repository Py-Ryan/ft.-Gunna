import asyncpg

from discord.ext import commands
from typing import Dict, List, Union, Optional
from ftg.extensions.utils.context import Context

from discord import (
    User,
    Role,
    Embed,
    Member,
    Forbidden,
    VoiceChannel,
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

        embed: Embed = Embed(title=f"Banned from '{ctx.guild.name}'.", colour=ctx.__randcolor__())
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

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, manage_roles=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def mute(self, ctx: Context, members: commands.Greedy[Member], *, reason: str = "None") -> None:
        failures: int = 0
        guild_mute_role: Optional[asyncpg.Record, Role] = await self.client.db.fetchrow(
            """
            SELECT (mute_role_id)
            FROM guilds
            WHERE id=$1
            """,
            ctx.guild.id
        )

        try:
            guild_mute_role = ctx.guild.get_role(int(guild_mute_role["mute_role_id"]))
        except TypeError:
            pass

        if not isinstance(guild_mute_role, Role):
            guild_mute_role = await ctx.guild.create_role(
                name="Gunna Muted",
                reason="No mute role has been configured for the guild. A default one has been created.",
            )

            for channel in ctx.guild.channels:
                overwrites = channel.overwrites_for(guild_mute_role)
                overwrites.send_messages, overwrites.add_reactions = False, False

                if isinstance(channel, VoiceChannel):
                    overwrites.speak = False

                try:
                    await channel.set_permissions(guild_mute_role, overwrite=overwrites)
                except HTTPException:
                    failures += 1

            await self.client.db.execute(
                """
                INSERT INTO guilds(id, mute_role_id)
                VALUES($1, $2)
                ON CONFLICT (id)
                DO UPDATE
                SET mute_role_id=$2
                """,
                ctx.guild.id,
                guild_mute_role.id,
            )

        if not members:
            await ctx.send(desc="Didn't get any members to mute.")
        else:
            for member in members:
                roles_excluding_everyone = \
                    [role for role in member.roles if role != ctx.guild.default_role]

                if member.roles:
                    await member.remove_roles(*roles_excluding_everyone)

                await member.add_roles(
                    guild_mute_role,
                    reason=f"Muted by {ctx.author} ({ctx.author.id}) | Reason: {reason}"
                )

                await self.client.db.execute(
                    """
                    INSERT INTO mute_manager (id, pre_mute_roles)
                    VALUES ($1, $2)
                    ON CONFLICT (id)
                    DO UPDATE
                    SET pre_mute_roles=$2
                    """,
                    member.id,
                    ",".join([str(role.id) for role in roles_excluding_everyone])
                )

            msg: str = "They're muted \U0001f44c"
            if failures:
                msg += f", but due to permission issues, they're still unmuted in {failures} channels."

            await ctx.send(desc=msg, reaction="\U00002705")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, manage_roles=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def unmute(self, ctx: Context, members: commands.Greedy[Member], *, reason: str = "None") -> None:
        pmr_roles_for_each: Dict[int, List[int]] = dict()
        guild_mute_role: asyncpg.Record = await self.client.db.fetchrow(
            """
            SELECT (mute_role_id)
            FROM guilds
            WHERE id=$1
            """,
            ctx.guild.id
        )

        if not guild_mute_role:
            await ctx.send(desc="There is no mute role for this server. Mute a member to create one automatically.")
            return

        if members or any(member.bot for member in members):
            for member in members:
                pmr_for_member: Optional[asyncpg.Record] = \
                    await self.client.db.fetchrow(
                        """
                        SELECT (pre_mute_roles)
                        FROM mute_manager
                        WHERE id=$1
                        """,
                        member.id
                    )

                try:
                    pmr_roles_for_each[member.id] = pmr_for_member["pre_mute_roles"].split(",")
                except TypeError:
                    pmr_roles_for_each[member.id] = None
                finally:
                    guild_mute_role = ctx.guild.get_role(int(guild_mute_role["mute_role_id"]))
                    await member.remove_roles(guild_mute_role)

                    if pmr_roles_for_each[member.id]:
                        pre_mute_roles: List[Role] = \
                            [
                                ctx.guild.get_role(int(role_id))
                                for role_id in pmr_roles_for_each[member.id]
                            ]

                        await member.add_roles(*pre_mute_roles)

                        await self.client.db.execute(
                            """
                            DELETE FROM mute_manager
                            WHERE id=$1
                            """,
                            member.id
                        )

            await ctx.send(desc="They're unmuted \U0001f44c", reaction="\U00002705")
        else:
            await ctx.send(desc="No member(s) to unmute.")


def setup(client: commands.Bot) -> None:
    client.add_cog(MemberCog(client))
