import os
from typing import Any, TYPE_CHECKING

import aiohttp
import discord
import elaina


class MyClient(discord.Client):
    """Discord client with custom ``aiohttp.ClientSession``
    and ``elaina.ElainaClient`` as attributes.
    """

    if TYPE_CHECKING:
        _elaina: elaina.ElainaClient
        session: aiohttp.ClientSession

    async def start(self, *args, **kwargs) -> None:
        async with aiohttp.ClientSession() as session:
            self._elaina = elaina.ElainaClient(session)
            self.session = session
            await super().start(*args, **kwargs)


client = MyClient()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message) -> Any:
    if message.author.bot:
        return

    answer = await client._elaina.get_answer(message.content)
    if answer:
        await message.channel.send(answer)


client.run(os.environ["TOKEN"])
