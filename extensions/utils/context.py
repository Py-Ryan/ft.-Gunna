import random
import inspect
import discord

from discord.ext import commands


class Context(commands.Context):
    """Customized context object. This only really adds quick reaction adding and easy embedding.

        Attributes
        ----------
        reactions (Dict[str, str]):
            'name' to 'unicode' pairs of reactions. Appear as 'check': "\U00002705"
        color_list (List[discord.Colour]):
            A list of returns from pre-defined color methods parsed from the discord.Colour class
    """

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
        """Return a random color from discord.Colour

            Returns
            -------
                discord.Colour
        """
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
        """Modified send method. Kwargs only.

            This is mainly used for setting brief description-only embeds with random colors.
            If you wish to pass a normal message, pass a 'content' kwarg.
            If you pass 'desc' as a kwarg, then all other kwargs go into embed constructor.
            To make use of instantly reacting to the command invocation message, pass a unicode to reaction kwarg.

            Returns
            -------
                discord.Message
        """
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
