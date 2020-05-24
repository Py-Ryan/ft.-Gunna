from discord.ext import commands
from .utils.context import Context
from typing import Optional, Union
from discord import (
    TextChannel,
    VoiceChannel,
    HTTPException,
    CategoryChannel
)


class ChannelCog(commands.Cog):

    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def channel(self,
                      ctx: Context,
                      name: str,
                      type_: str,
                      category: Optional[CategoryChannel],
                      *,
                      topic: Optional[str],
                      ) -> None:
        reason = f'Created by {ctx.author} ({ctx.author.id})'

        try:
            if type_.lower() in 'vcvoicechannel':
                await ctx.guild.create_voice_channel(
                    name,
                    category=category,
                    reason=reason
                )
            else:
                await ctx.guild.create_text_channel(
                    name,
                    category=category,
                    topic=topic,
                    reason=reason
                )
        except HTTPException:
            await ctx.send(
                desc="An HTTP error prevented me from creating a new channel.",
                reaction="\U0000274c"
            )
        else:
            await ctx.send(
                desc=f"Successfully created a channel named {name} \U0001f44c",
                reaction="\U00002705"
            )

    @channel.command()
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def delete(self,
                     ctx: Context,
                     channel: Union[TextChannel, VoiceChannel, CategoryChannel],
                     *,
                     reason: Optional[str]) -> None:
        reason = f'Deleted by {ctx.author} ({ctx.author.id}) | Reason: {reason}'

        try:
            await channel.delete(reason=reason)
        except HTTPException:
            await ctx.send(
                desc="An HTTP error prevented me from deleted the channel.",
                reaction="\U0000274c"
            )
        else:
            await ctx.send(
                desc=f"Successfully deleted channel {channel.name} \U0001f44c",
                reaction="\U00002705"
            )


def setup(client: commands.Bot) -> None:
    client.add_cog(ChannelCog(client))
