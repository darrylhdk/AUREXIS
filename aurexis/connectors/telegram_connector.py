"""
AUREXIS - Telegram Connector
Architecture: Telegram → Webhook → Orchestrator → LLM → Response
"""
import asyncio
import logging
from core.auth import KeyVault

logger = logging.getLogger(__name__)


class TelegramConnector:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.token = KeyVault().get_key("telegram") or ""

    async def start(self):
        if not self.token:
            logger.warning("Telegram token not set. Skipping.")
            return
        from telegram import Update
        from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

        async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
            text = update.message.text
            response = await self.orchestrator.process(text)
            await update.message.reply_text(response)

        app = ApplicationBuilder().token(self.token).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        logger.info("Telegram connector started")
        await app.run_polling()
