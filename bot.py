import logging
from db import init_db, add_user
from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.utils.request import Request
from echo.config import load_config
from echo.utils import logger_factory

config = load_config()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
debug_requests = logger_factory(logger=logger)


@debug_requests
def message_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    if user:
        name = user.first_name
    else:
        name = 'аноним'

    text = update.effective_message.text
    reply_text = f'Привет, {name}!\n\n{text}'

    # # Ответить пользователю
    # update.message.reply_text(
    #     text=reply_text,
    #     reply_markup=get_keyboard(),
    # )

    # Записать сообщение в БД
    # if text:
    #     add_user()


def main():
    logger.info('Start EnglishBot')

    req = Request(connect_timeout=0.5, read_timeout=1.0)
    bot = Bot(
        token='1167357128:AAHCB0nLfQigtx9Lnu6nKPW-V53e47_tCZ0',
        request=req,
        # base_url='https://telegg.ru/orig/bot'
    )
    updater = Updater(
        bot=bot,
        use_context=True
    )

    # Проверка на корректное подключение к Telegram API
    info = bot.get_me()
    logger.info(f'Bot information: {info}')

    # Подключение к СУБД
    init_db()


    # Повесить обработчики команд
    handler = MessageHandler(Filters.all, message_handler)
    updater.dispatcher.add_handler(handler)


if __name__ == '__main__':
    main()
