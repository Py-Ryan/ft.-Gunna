from discord.ext import commands, tasks
from collections import namedtuple, deque


class EventsCog(commands.Cog):
    """Extension for handling events and features corresponding to these events"""

    __slots__ = "client"

    def __init__(self, client):
        self.client = client

        @tasks.loop(seconds=15)
        async def _clear_deleted_message_cache(inst):
            # This doesn't work, I don't know why.
            for guild in inst.client.cache["messages"]:
                if guild:
                    for i in range(1, 5):
                        guild.pop()

        _clear_deleted_message_cache.start(self)

    message_data = namedtuple('message_data', ['content', 'author', 'type'])

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """The following features are handled:

            Updating the deleted message cache.
        """

        info = type(self).message_data(
            content=message.content,
            author=message.author.id,
            type='delete'
        )
        cache = self.client.cache["messages"].setdefault(str(message.guild.id), deque())
        cache.appendleft(info)


def setup(client):
    client.add_cog(EventsCog(client))
