import os
import asyncio

import discord
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

"autogen-rag"

# Your bot's token
TOKEN = os.environ.get("DISCORD_TOKEN")
SERVER_ID = os.environ.get("DISCORD_SERVER_ID")


intents = discord.Intents.default()
intents.messages = True  # Enables the bot to receive messages
client = discord.Client(intents=intents)

async def fetch_all_channel_history():
    await client.wait_until_ready()
    server = client.get_guild(int(SERVER_ID))
    if not server:
        print(f"Server with ID {SERVER_ID} not found.")
        return

    for channel in server.text_channels:
        print(f"Fetching history for channel: {channel.name}")
        try:
            async for message in channel.history(limit=None):
                # Do something with each message, e.g., print or save to a file
                print(message.content)
        except discord.errors.Forbidden:
            print(f"Do not have permissions to access channel: {channel.name}")

client.loop.create_task(fetch_all_channel_history())
client.run(TOKEN)
