import json

from typing import Union
from discord.ext import commands

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
    """Extension designated for commands that interact with members."""

    __slots__ = "client"

    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def kick(self, ctx, members: commands.Greedy[Member], *, reason="None"):
        """Kick a member(s) from a guild."""

        embed = Embed(title="Kicked.", colour=ctx.__randcolor__())
        embed.add_field(name="Kicked By:", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        embed.add_field(name="Reason:", value=reason, inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)

        if members:
            curr_member = None
            try:
                for member in members:
                    curr_member = member
                    await ctx.guild.kick(
                        curr_member,
                        reason=f"Kicked By: {ctx.author}({ctx.author.id}) | Reason: {reason}",
                    )
            except HTTPException:
                raise commands.CommandError(f"I'm unable to kick {curr_member}.")
            else:
                await ctx.send(desc=f"They're gone {ctx.reactions.get('ok')}", reaction=ctx.reactions.get("check"))
        else:
            raise commands.BadArgument("No user(s) were provided to kick.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def ban(self, ctx, users: commands.Greedy[Union[Member, User, int]], *, rsn="None"):
        """Ban a user(s) from a guild. Supports hackbanning by ID."""

        if isinstance(users, list):
            for user_ in range(len(users)):
                if isinstance(users[user_], int):
                    users[user_] = Snowflake(id=users[user_])
        elif isinstance(users, int):
            users = Snowflake(id=users)

        embed = Embed(title=f"Banned from '{ctx.guild.name}'.", colour=ctx.__randcolor__())
        embed.add_field(name="Banned By:", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        embed.add_field(name="Reason:", value=rsn, inline=False)
        embed.set_thumbnail(url=ctx.guild.icon_url)

        curr_user = None
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

            raise commands.CommandError(f"I'm unable to ban {curr_user}.")
        else:
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

            await ctx.send(desc=f"They're gone {ctx.reactions.get('ok')}", reaction=ctx.reactions.get("check"))

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, manage_roles=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def mute(self, ctx, members: commands.Greedy[Member], *, reason="None"):
        """Mute member(s) in the guild."""

        failures = 0
        mute_metadata = await self.client.db.fetchrow(
            """
            SELECT (mute_metadata)
            FROM guilds
            WHERE id = $1
            """,
            ctx.guild.id
        )

        if not mute_metadata or mute_metadata["mute_metadata"] is None:
            mute_metadata = '{"mute_metadata": {"mute_role_id": 0, "muted_members": {}}}'
        else:
            mute_metadata = mute_metadata["mute_metadata"]

        try:
            mute_metadata = json.loads(mute_metadata)["mute_metadata"]
        except KeyError:
            mute_metadata = json.loads(mute_metadata)

        guild_mute_role = None

        try:
            guild_mute_role = ctx.guild.get_role(int(mute_metadata["mute_role_id"]))
        except (TypeError, KeyError):
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

            mute_metadata["mute_role_id"] = guild_mute_role.id

            await self.client.db.execute(
                """
                UPDATE guilds
                SET mute_metadata = $2
                WHERE id = $1
                """,
                ctx.guild.id,
                json.dumps(mute_metadata)
            )

        if not members:
            raise commands.BadArgument("No user(s) were provided to mute.")
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

                mute_metadata["muted_members"][member.id] = {
                    "muted_by": ctx.author.id,
                    "muted_for": reason,
                    "time_left": 'Not timed',
                    "pre_mute_roles": ",".join([str(role.id) for role in roles_excluding_everyone])
                }
                await self.client.db.execute(
                    """
                    UPDATE guilds
                    SET mute_metadata = $2
                    WHERE id = $1
                    """,
                    ctx.guild.id,
                    json.dumps(mute_metadata)
                )

            msg = f"They're muted {ctx.reactions.get('ok')}"
            if failures:
                msg += f", but due to permission issues, they're still unmuted in {failures} channels."

            await ctx.send(desc=msg, reaction=ctx.reactions.get("check"))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True, manage_roles=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def unmute(self, ctx, members: commands.Greedy[Member], *, reason="None"):
        """Unmute member(s) in the guild."""

        pmr_roles_for_each = {}
        mute_metadata = await self.client.db.fetchrow(
            """
            SELECT (mute_metadata)
            FROM guilds
            WHERE id=$1
            """,
            ctx.guild.id
        )

        try:
            mute_metadata = json.loads(mute_metadata["mute_metadata"])
        except (KeyError, TypeError):
            mute_metadata = json.loads(mute_metadata)

        if not mute_metadata or not mute_metadata["mute_role_id"]:
            raise commands.CommandError("There is no mute metadata for this server. Mute someone first.")

        if members or any(member for member in members if not member.bot):
            for member in members:
                try:
                    pmr_for_member = mute_metadata["muted_members"][str(member.id)]["pre_mute_roles"]
                except KeyError:
                    break

                try:
                    pmr_roles_for_each[member.id] = pmr_for_member.split(",") if pmr_for_member else None
                except TypeError:
                    pmr_roles_for_each[member.id] = None
                finally:
                    guild_mute_role = ctx.guild.get_role(int(mute_metadata["mute_role_id"]))

                    await member.remove_roles(guild_mute_role)

                    if pmr_roles_for_each[member.id]:
                        pre_mute_roles = \
                            [
                                ctx.guild.get_role(int(role_id))
                                for role_id in pmr_roles_for_each[member.id]
                            ]

                        await member.add_roles(*pre_mute_roles)

                    del mute_metadata["muted_members"][str(member.id)]
                    await self.client.db.execute(
                        """
                        UPDATE guilds
                        SET mute_metadata = $1
                        WHERE id = $2
                        """,
                        json.dumps(mute_metadata),
                        ctx.guild.id
                    )

            await ctx.send(desc="They're unmuted \U0001f44c", reaction="\U00002705")
        else:
            raise commands.BadArgument("No member(s) to unmute")

    @mute.command()
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def info(self, ctx, member: Member):
        """Show info regarding a mute on a member."""

        data = await self.client.db.fetchrow(
            """
            SELECT mute_metadata
            FROM guilds
            WHERE id = $1
            """,
            ctx.guild.id
        )

        if data or data["mute_metadata"]:
            data = json.loads(data["mute_metadata"])

            if str(member.id) in data["muted_members"]:
                entry = data["muted_members"][str(member.id)]
                muted_by = self.client.get_user(entry["muted_by"])
                muted_for = entry["muted_for"]
                time_left = entry["time_left"]

                info_embed: Embed = Embed(description=f"Mute info on {member}", colour=ctx.__randcolor__())
                info_embed.add_field(name=f"Muted By:", value=f"{muted_by} ({muted_by.id})", inline=True)
                info_embed.add_field(name="Time Left:", value=time_left, inline=False)
                info_embed.add_field(name="Reason:", value=muted_for)
                info_embed.set_thumbnail(url=member.avatar_url)

                await ctx.send(embed=info_embed, reaction=ctx.reactions.get("check"))
        else:
            raise commands.CommandError("There is no mute metadata for this server. Mute someone first.")


def setup(client):
    client.add_cog(MemberCog(client))
