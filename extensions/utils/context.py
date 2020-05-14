import random
import inspect
import discord
from discord.ext import commands
from typing import Any, Dict, List, Optional


class Context(commands.Context):
    """Custom context object."""

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        self.color_list: List[discord.Colour] = list()
        super().__init__(**kwargs)

    def __randcolor__(self) -> discord.Colour:
        """Return a random color from discord.Colour"""
        if not self.color_list:
            for member in dir(discord.Colour):
                try:
                    attribute: Any = getattr(discord.Colour, member)
                    if inspect.ismethod(attribute):
                        rt: Any = attribute()
                        if isinstance(rt, discord.Colour):
                            self.color_list.append(rt)
                except TypeError:
                    pass

        return random.choice(self.color_list)

    async def send(self, **kwargs: Optional[Dict[str, Any]]) -> discord.Message:
        msg: Optional[discord.Message] = None

        try:
            await self.message.add_reaction(kwargs.pop('reaction'))
        except KeyError:
            pass

        try:
            desc: str = kwargs.pop("desc")
            try:
                colour: discord.Colour = kwargs.pop("colour")
            except KeyError:
                colour = self.__randcolor__()
            msg = await super().send(embed=discord.Embed(description=f'**{desc}**', colour=colour), **kwargs)
        except KeyError:
            msg = await super().send(**kwargs)

        return msg
