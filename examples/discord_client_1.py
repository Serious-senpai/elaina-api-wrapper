import os
from typing import Any

import discord
import elaina


client = discord.Client()
elaina_client = elaina.ElainaClient()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message) -> Any:
    if message.author.bot:
        return

    answer = await elaina_client.get_answer(message.content)
    if answer:
        await message.channel.send(answer)


client.run(os.environ["TOKEN"])
