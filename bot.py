# ================= standart modules =====================
import logging
import re
import os
# ==================== My modules ========================
from db import (init_db, add_user_to_db, get_user_from_db,
                delete_user_from_db, get_lvl, get_info_from_db)
import constants
from echo.config import load_config
from echo.utils import logger_factory
# ================= python-telegram-bot library ==========
from telegram import Bot
from telegram import Update
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.utils.request import Request

#
# print(os.environ.get('TG_CONF'))
# config = load_config()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
debug_requests = logger_factory(logger=logger)


@debug_requests
def keyboard_handler(update: Update, context: CallbackContext):
    """
    Обработка нажатий на кнопки клавиатуры
    """
    # При каждом нажатии на кнопку Telegram будет присылать callback_query
    # Идентификатор нажатой кнопки (callback_query.data)
    query = update.callback_query
    data = query.data

    if data == constants.CALLBACK_BUTTON_START:







@debug_requests
def start_handler(update: Update, context: CallbackContext):
    """
    Начало работы бота.
    Если юзер был зарегистрирован, то он удаляется с таблицы users.
    """
    user_id = update.effective_user.id
    if get_user_from_db(user_id=user_id) is not None:
        delete_user_from_db(user_id=user_id)
    update.message.reply_markdown(text=constants.greeting_msg)


@debug_requests
def help_handler(update: Update, context: CallbackContext):
    """
    Описание бота.
    """
    update.message.reply_markdown(text=constants.help_msg)



@debug_requests
def plan_handler(update: Update, context: CallbackContext):
    """
    Описание тем обучения.
    """
    update.message.reply_markdown(text=constants.plan_msg)


@debug_requests
def get_lvl_handler(update: Update, context: CallbackContext):
    """
    Получение уровня пользователя
    """
    update.message.reply_text(text=f"Ваш уровень: {get_lvl(user_id=update.effective_user.id)}")


#  <============================== Для регистрации в боте ========================================>
@debug_requests
def registr_handler(update: Update, context: CallbackContext):
    """
    Начало регистрации в боте и проверка на наличие юзера в БД
    :return: constants.NAME
    """
    if get_user_from_db(user_id=update.effective_user.id) is not None:
        update.message.reply_text(text="Вы уже зарегистрированы в боте!")
        return ConversationHandler.END

    update.message.reply_text(text="Введите своё имя.")
    return constants.NAME


@debug_requests
def name_handler(update: Update, context: CallbackContext):
    """
    Получить имя и записать в словарь, который передается от функции к функции, где есть 'pass_user_data=True'
    :return: constants.SURNAME
    """
    # Проверка на правильность ввода ИМЕНИ
    if re.search(r'\d|\W', update.message.text) is not None:
        update.message.reply_text(text="Введите корректное имя!")
        return constants.NAME

    context.user_data['NAME'] = update.message.text
    logger.info(f'user_data: {context.user_data}')

    # Спросить фамилию
    update.message.reply_text(text="Введите свою фамилию.")
    return constants.SURNAME


@debug_requests
def surname_handler(update: Update, context: CallbackContext):
    """
    Получить фамилию и записать в словарь.
    Из словаря записать все данные в БД.
    :return: ConversationHandler.END
    """
    # Проверка на правильность ввода ФАМИЛИИ
    if re.search(r'\d|\W', update.message.text) is not None:
        update.message.reply_text(text="Введите корректную фамилию!")
        return constants.SURNAME

    # Получить фамилию и записать в словарь
    context.user_data['SURNAME'] = update.message.text
    logger.info(f'user_data: {context.user_data}')

    # Записать из словаря в БД
    add_user_to_db(
        first_name=context.user_data['NAME'],
        last_name=context.user_data['SURNAME'],
        user_id=update.effective_user.id
    )

    context.user_data.clear()
    update.message.reply_text(text="Вы успешно зарегистрированы!")
    update.message.reply_markdown(
        text=constants.after_reg_msg,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=constants.TITLES[constants.CALLBACK_BUTTON_START],
                                         callback_data=constants.CALLBACK_BUTTON_START)
                ],
            ],
        )
    )

    return ConversationHandler.END


@debug_requests
def cancel_handler(update: Update, context: CallbackContext):
    """
    Отмена всего диалога, данные будут утеряны
    """
    update.message.reply_text(text='Отмена.\nДля регистрации с нуля нажмите /reg')
    return ConversationHandler.END
#  <========================================================================================>



# @debug_requests
# def message_handler(update: Update, context: CallbackContext):
#     name = update
#     user = update.effective_user
#     if user:
#         name = user.first_name
#     else:
#         name = 'аноним'
#
#     text = update.effective_message.text
#     reply_text = f'Привет, {name}!\n\n{text}'
#
#     # # Ответить пользователю
#     # update.message.reply_text(
#     #     text=reply_text,
#     #     reply_markup=get_keyboard(),
#     # )
#
#     # Записать сообщение в БД
#     # if text:
#     #     add_user_to_db()

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
    handler_start = CommandHandler('start', start_handler)
    updater.dispatcher.add_handler(handler_start)

    handler_help = CommandHandler('help', help_handler)
    updater.dispatcher.add_handler(handler_help)

    handler_plan = CommandHandler('plan', plan_handler)
    updater.dispatcher.add_handler(handler_plan)

    handler_lvl = CommandHandler('level', get_lvl_handler)
    updater.dispatcher.add_handler(handler_lvl)

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('reg', registr_handler, pass_user_data=True)
        ],
        states={
            constants.NAME: [
                MessageHandler((Filters.text & (~Filters.command)), name_handler, pass_user_data=True)
            ],
            constants.SURNAME: [
                MessageHandler((Filters.text & (~Filters.command)), surname_handler, pass_user_data=True)
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler)
        ]
    )
    updater.dispatcher.add_handler(conv_handler)

    # Бесконечная обработка входящих сообщений
    updater.start_polling()
    updater.idle()
    logger.info('Stop EnglishBot')


if __name__ == '__main__':
    main()
