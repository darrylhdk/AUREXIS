"""
AUREXIS - Discord Connector
"""
import logging
from core.auth import KeyVault

logger = logging.getLogger(__name__)


class DiscordConnector:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.token = KeyVault().get_key("discord") or ""

    async def start(self):
        if not self.token:
            logger.warning("Discord token not set. Skipping.")
            return
        import discord

        intents = discord.Intents.default()
        intents.message_content = True
        client = discord.Client(intents=intents)

        @client.event
        async def on_message(message):
            if message.author == client.user:
                return
            if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
                response = await self.orchestrator.process(message.content)
                await message.channel.send(response)

        logger.info("Discord connector started")
        await client.start(self.token)
