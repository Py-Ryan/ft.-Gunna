import random
import inspect
import discord

from discord.ext import commands


class Context(commands.Context):
    """Custom context object."""

    __slots__ = ("color_list", "reactions")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color_list = []
        self.reactions = {
            'check': "\U00002705",
            'x': "\U0000274c",
            'ok': "\U0001f44c"
        }

    def __randcolor__(self):
        """Return a random color from discord.Colour"""
        if not self.color_list:
            for member in dir(discord.Colour):
                try:
                    attribute = getattr(discord.Colour, member)
                    if inspect.ismethod(attribute):
                        rt = attribute()
                        if isinstance(rt, discord.Colour):
                            self.color_list.append(rt)
                except TypeError:
                    pass

        return random.choice(self.color_list)

    async def send(self, **kwargs):
        msg = None

        try:
            await self.message.add_reaction(kwargs.pop("reaction"))
        except KeyError:
            pass

        try:
            desc = kwargs.pop("desc")
            colour = kwargs.pop("colour", None) or self.__randcolor__()

            msg = await super().send(
                embed=discord.Embed(description=f"**{desc}**", colour=colour, **kwargs)
            )
        except KeyError:
            msg = await super().send(**kwargs)

        return msg
