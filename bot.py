# ================= standart modules =====================
import logging
import re
# ==================== My modules ========================
from db import (init_db, add_user_to_db, get_user_from_db,
                delete_user_from_db, get_lvl, inc_lvl,
                get_info_from_db, get_tests_from_db)
import constants
import parse
from echo.config import load_config
from echo.utils import logger_factory
# ================= python-telegram-bot library ==========
from telegram import Bot
from telegram import Update
from telegram import Sticker
from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ParseMode
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.utils.request import Request


# print(os.environ.get('TG_CONF'))
# config = load_config()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
debug_requests = logger_factory(logger=logger)
sub_count = 0           # Для счета подтем
quest_count = 0         # Для счета вопросов
quest_used = list()     # Список использованных вопросов
correct_ans_count = 0   # Для подсчета правильных ответов
flag_shutup = 0         # Для отсчета присланных юзером ненужных сообщений

#  <=========================== Inline и Reply клавиатуры =========================================>
@debug_requests
def get_start_inline_keyboard(link: str):
    """
    Получить клавиатуру при обзоре 1-й подтемы
    """
    keyboard = [
        # В этом списке каждый список - это строка,
        # В каждом списке находяться кнопки. Сколько кнопок, столько столбцов
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_LINK],
                                 url=link)
        ],
        [
          InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_NEXT],
                               callback_data=constants.CALLBACK_BUTTON_NEXT)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

@debug_requests
def get_middle_inline_keyboard(link: str):
    """
    Получить клавиатуру при обзоре тем между 1-й и последней подтемами
    """
    keyboard = [
        # В этом списке каждый список - это строка,
        # В каждом списке находяться кнопки. Сколько кнопок, столько столбцов
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_LINK],
                                 url=link)
        ],
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_BACK],
                                 callback_data=constants.CALLBACK_BUTTON_BACK),
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_NEXT],
                                 callback_data=constants.CALLBACK_BUTTON_NEXT)
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

@debug_requests
def get_finish_inline_keyboard(link: str):
    """
    Получить клавиатуру при обзоре последней подтемы
    """
    keyboard = [
        # В этом списке каждый список - это строка,
        # В каждом списке находяться кнопки. Сколько кнопок, столько столбцов
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_LINK],
                                 url=link)
        ],
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_TEST],
                                 callback_data=constants.CALLBACK_BUTTON_TEST),
        ],
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_BACK],
                                 callback_data=constants.CALLBACK_BUTTON_BACK),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


@debug_requests
def get_inline_keyboard_for_tests():
    """
    Получить клавиатуру с вариантами ответов в тестах
    """
    keyboard = [
        # В этом списке каждый список - это строка,
        # В каждом списке находяться кнопки. Сколько кнопок, столько столбцов
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_VAR1],
                                 callback_data=constants.CALLBACK_BUTTON_VAR1),
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_VAR2],
                                 callback_data=constants.CALLBACK_BUTTON_VAR2)
        ],
        [
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_VAR3],
                                 callback_data=constants.CALLBACK_BUTTON_VAR3),
            InlineKeyboardButton(constants.TITLES[constants.CALLBACK_BUTTON_VAR4],
                                 callback_data=constants.CALLBACK_BUTTON_VAR4)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

@debug_requests
def get_button_new_theme():
    """
    Получить кнопку после правильных ответов на тесты
    """
    keyboard = [
        [
            InlineKeyboardButton(text=constants.BUTTON_TITLE_NEW_THEME,
                                 callback_data=constants.CALLBACK_BUTTON_START)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

@debug_requests
def get_button_old_theme():
    """
    Получить кнопку после неправильных ответов на тесты
    """
    keyboard = [
        [
            InlineKeyboardButton(text=constants.BUTTON_TITLE_OLD_THEME,
                                 callback_data=constants.CALLBACK_BUTTON_START)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
#  <========================================================================================>


#  <=============== Обработка нажатий на кнопки Inline-клавиатуры =====================>
@debug_requests
def keyboard_handler(update: Update, context: CallbackContext):
    """
    Обработка нажатий на кнопки клавиатуры
    """
    user_id = update.effective_user.id

    # Получаем всю информацию по теме в зависимости от уровня пользователя
    theme, tup_subthemes, descrp_dict, links_dict = get_info_from_db(user_id=user_id)
    last_index = len(tup_subthemes)-1   # Последний индекс кортежа из подтем

    # Получаем все вопросы и ответы на них в зависимости от прошедшей темы
    quest_ans, questions, correct_ans = get_tests_from_db(user_id=user_id)
    context.user_data['QUEST_ANS'] = quest_ans
    context.user_data['QUESTIONS'] = questions
    context.user_data['CORRECT_ANS'] = correct_ans

    # При каждом нажатии на кнопку Telegram будет присылать callback_query
    # Идентификатор нажатой кнопки (callback_query.data)
    query = update.callback_query
    data = query.data

    if data == constants.CALLBACK_BUTTON_START:
        global sub_count
        print("Нажал на START. sub_count стал ", sub_count)
        subtheme = tup_subthemes[sub_count]
        info = f'*{theme}*\n\n_{subtheme}_\n\n{descrp_dict[subtheme]}'
        update.effective_message.reply_markdown(
            text=info,
            reply_markup=get_start_inline_keyboard(links_dict[subtheme])
        )
        print("Отработал START\n")

    elif data == constants.CALLBACK_BUTTON_NEXT:
        sub_count += 1

        if sub_count > last_index:      # Для того, чтобы счет подтем не выходил
            sub_count = last_index      # за пределы количества подтем (длины кортежа)
        print("Нажал на NEXT. sub_count стал ", sub_count)

        subtheme = tup_subthemes[sub_count]
        info = f'*{theme}*\n\n_{subtheme}_\n\n{descrp_dict[subtheme]}'
        if sub_count < last_index:
            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_middle_inline_keyboard(links_dict[subtheme])
            )
        elif sub_count == last_index:
            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_finish_inline_keyboard(links_dict[subtheme])
            )
        print("Отработал NEXT\n")

    elif data == constants.CALLBACK_BUTTON_BACK:
        sub_count -= 1

        if sub_count <= 0:      # Для того, чтобы счет подтем не был меньше 0
            sub_count = 0
        print("Нажал на BACK. sub_count стал ", sub_count)

        subtheme = tup_subthemes[sub_count]
        info = f'*{theme}*\n\n_{subtheme}_\n\n{descrp_dict[subtheme]}'
        if sub_count > 0:
            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_middle_inline_keyboard(links_dict[subtheme])
            )
        elif sub_count == 0:
            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_start_inline_keyboard(links_dict[subtheme])
            )
        print("Отработал BACK \n")

    elif data == constants.CALLBACK_BUTTON_TEST:
        print("Нажал на TEST.")
        sub_count = 0       # Обнуляем, чтобы новое открытие тем не было с конца
        global quest_count
        global quest_used
        quest_used = []
        quest_count, ans_var, text = parse.get_test_msg(
            questions=questions,
            quest_ans=quest_ans,
            quest_used=quest_used,
            quest_count=quest_count
        )

        context.user_data['ANS_VAR'] = ans_var
        update.effective_message.delete()
        update.effective_message.reply_markdown(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )
        print("Отработал TEST \n")
        context.chat_data['in_conv_test'] = True
        return constants.VARS


@debug_requests
def button_vars_handler(update: Update, context: CallbackContext):
    """
    Обработка нажатий на кнопки (варианты ответов) в тестах
    """
    if not context.chat_data['in_conv_test']:
        return ConversationHandler.END
    # При каждом нажатии на кнопку Telegram будет присылать callback_query
    # Идентификатор нажатой кнопки (callback_query.data)
    query = update.callback_query
    data = query.data

    ans_var = context.user_data['ANS_VAR']
    questions = context.user_data['QUESTIONS']
    quest_ans = context.user_data['QUEST_ANS']
    correct_ans = context.user_data['CORRECT_ANS']

    if data == constants.CALLBACK_BUTTON_VAR1:
        print("Нажал на VAR1.")
        global quest_count
        global quest_used
        global correct_ans_count

        quest_count, correct_ans_count, ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=quest_used,
            quest_count=quest_count,
            correct_ans_count=correct_ans_count
        )
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if quest_count == 0:                                # Когда закончились вопросы
            for i in range(len(correct_ans)):               # Для удаления всех ответов пользователя
                query.message.delete()
                update.effective_message.message_id -= 1
            if correct_ans_count == len(correct_ans):       # Если все ответы верны
                inc_lvl(user_id=update.effective_user.id)
                update.effective_message.reply_markdown(text=constants.congrat_msg)
                update.effective_message.reply_markdown(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif correct_ans_count != len(correct_ans):     # Если хоть один ответ не верный
                update.effective_message.reply_markdown(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(correct_ans_count))
            correct_ans_count = 0
            return ConversationHandler.END
        update.effective_message.reply_markdown(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )

        print("Отработал VAR1 \n")

    elif data == constants.CALLBACK_BUTTON_VAR2:
        print("Нажал на VAR2.")
        quest_count, correct_ans_count, ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=quest_used,
            quest_count=quest_count,
            correct_ans_count=correct_ans_count
        )
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if quest_count == 0:
            for i in range(len(correct_ans)):
                query.message.delete()
                update.effective_message.message_id -= 1
            if correct_ans_count == len(correct_ans):
                inc_lvl(user_id=update.effective_user.id)
                update.effective_message.reply_markdown(text=constants.congrat_msg)
                update.effective_message.reply_markdown(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif correct_ans_count != len(correct_ans):
                update.effective_message.reply_markdown(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(correct_ans_count))
            correct_ans_count = 0
            return ConversationHandler.END
        update.effective_message.reply_markdown(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )
        print("Отработал VAR2 \n")

    elif data == constants.CALLBACK_BUTTON_VAR3:
        print("Нажал на VAR3.")
        quest_count, correct_ans_count, ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=quest_used,
            quest_count=quest_count,
            correct_ans_count=correct_ans_count
        )
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if quest_count == 0:
            for i in range(len(correct_ans)):
                query.message.delete()
                update.effective_message.message_id -= 1
            if correct_ans_count == len(correct_ans):
                inc_lvl(user_id=update.effective_user.id)
                update.effective_message.reply_markdown(text=constants.congrat_msg)
                update.effective_message.reply_markdown(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif correct_ans_count != len(correct_ans):
                update.effective_message.reply_markdown(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(correct_ans_count))
            correct_ans_count = 0
            return ConversationHandler.END
        update.effective_message.reply_markdown(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )
        print("Отработал VAR3 \n")

    elif data == constants.CALLBACK_BUTTON_VAR4:
        print("Нажал на VAR4.")
        # Проверка ответа пользователя
        quest_count, correct_ans_count, ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=quest_used,
            quest_count=quest_count,
            correct_ans_count=correct_ans_count
        )
        # Ответ от бота
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if quest_count == 0:
            for i in range(len(correct_ans)):
                query.message.delete()
                update.effective_message.message_id -= 1
            if correct_ans_count == len(correct_ans):
                inc_lvl(user_id=update.effective_user.id)
                update.effective_message.reply_markdown(text=constants.congrat_msg)
                update.effective_message.reply_markdown(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif correct_ans_count != len(correct_ans):
                update.effective_message.reply_markdown(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(correct_ans_count))
            correct_ans_count = 0
            return ConversationHandler.END
        update.effective_message.reply_markdown(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )
        print("Отработал VAR4 \n")

    print("Conversation --- CONTINUE {}\n".format(correct_ans_count))
    return constants.VARS
#  <========================================================================================>


@debug_requests
def start_handler(update: Update, context: CallbackContext):
    """
    Начало работы бота.
    Если юзер был зарегистрирован, то он удаляется с таблицы users.
    """
    user_id = update.effective_user.id
    if get_user_from_db(user_id=user_id) is not None:
        delete_user_from_db(user_id=user_id)
        update.message.reply_markdown(text=constants.del_user_msg)
    else:
        update.message.reply_markdown(text=constants.greeting_msg)
    try:
        if context.chat_data['in_conv_reg'] or context.chat_data['in_conv_test']:    # Если в диалоге, то отменить диалог
            context.chat_data['in_conv_reg'] = False
            context.chat_data['in_conv_test'] = False
            return ConversationHandler.END
    except KeyError:
        pass


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
    lvl = get_lvl(user_id=update.effective_user.id)
    if isinstance(lvl, int):
        update.message.reply_text(text=f"Ваш уровень: {lvl}")
    elif isinstance(lvl, str):
        update.message.reply_text(text=lvl)


@debug_requests
def shut_up_handler(update: Update, context: CallbackContext):
    """
    SHUT UP!!
    """
    global flag_shutup
    # user_id = update.effective_user.id
    # text = update.effective_message.text
    #
    # if user_id == 357912833:
    #     update.effective_message.bot.send_message(chat_id=429623673, text=text)

    if flag_shutup < 2:
        flag_shutup += 1
    else:
        update.effective_message.reply_sticker(
            sticker=Sticker(
                file_id='CAACAgIAAxkBAAIEa17LHgIb22R-EgkdalwzI327QeVAAAK-AAMw1J0RtKcIkYQmscoZBA',
                file_unique_id='AgADvgADMNSdEQ',
                width=512,
                height=512,
                is_animated=True
            )
        )
        flag_shutup = 0


#  <============================== Для регистрации в боте ========================================>
@debug_requests
def registr_handler(update: Update, context: CallbackContext):
    """
    Начало регистрации в боте и проверка на наличие юзера в БД
    :return: constants.NAME
    """
    context.chat_data['in_conv_reg'] = True
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
    context.chat_data['in_conv_reg'] = False
    return ConversationHandler.END


@debug_requests
def cancel_handler(update: Update, context: CallbackContext):
    """
    Отмена всего диалога, данные будут утеряны
    """
    try:
        if context.chat_data['in_conv_reg']:
            update.message.reply_text(text='Отмена.\nДля регистрации с нуля нажмите /reg')
            context.chat_data['in_conv_reg'] = False
    except KeyError:
        pass

    try:
        if context.chat_data['in_conv_test']:
            update.message.reply_markdown(
                text='Отмена теста.\nПожалуйста, пройдите заново материал.',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=constants.BUTTON_TITLE_AGAIN,
                                                 callback_data=constants.CALLBACK_BUTTON_START)
                        ],
                    ],
                )
            )
            context.chat_data['in_conv_test'] = False
    except Exception as e:
        print(e)

    return ConversationHandler.END
#  <========================================================================================>




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
    # init_db()

    # Повесить обработчики команд
    # сначала для ConversationHandler, потом остальные, потому что не работает тогда выход из диалога
    handler_reg = ConversationHandler(
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
            CommandHandler('cancel', cancel_handler),
            CommandHandler('start', start_handler)
        ]
    )
    updater.dispatcher.add_handler(handler_reg)

    handler_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(callback=keyboard_handler, pass_user_data=True)
        ],
        states={
            constants.VARS: [
                CallbackQueryHandler(callback=button_vars_handler, pass_user_data=True)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
            CommandHandler('start', start_handler)
        ],
        # per_message=True
    )
    updater.dispatcher.add_handler(handler_conv)

    handler_start = CommandHandler('start', start_handler)
    updater.dispatcher.add_handler(handler_start)

    handler_help = CommandHandler('help', help_handler)
    updater.dispatcher.add_handler(handler_help)

    handler_plan = CommandHandler('plan', plan_handler)
    updater.dispatcher.add_handler(handler_plan)

    handler_lvl = CommandHandler('level', get_lvl_handler)
    updater.dispatcher.add_handler(handler_lvl)

    handler_shutup = MessageHandler(Filters.all, shut_up_handler)
    updater.dispatcher.add_handler(handler_shutup)



    # Бесконечная обработка входящих сообщений
    updater.start_polling()
    updater.idle()
    logger.info('Stop EnglishBot')


if __name__ == '__main__':
    main()
