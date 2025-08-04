from telegram import Bot
from logger import log_info, log_error

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_message(self, message):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=message)
            log_info("Повідомлення надіслано у Telegram")
        except Exception as e:
            log_error(f"Telegram помилка: {e}")
