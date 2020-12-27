# ================= standard modules =====================
import logging
import re
# ==================== My modules ========================
from db import (init_db, add_user_to_db, get_user_from_db,
                delete_user_from_db, get_lvl, inc_lvl,
                get_info_from_db, get_tests_from_db, set_lvl)
import constants
import parse
# from echo.config import load_config
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
def get_finish_keyboard_changed_theme(link: str):
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
            InlineKeyboardButton(constants.BUTTON_TITLE_RET_THEME,
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

    # При каждом нажатии на кнопку Telegram будет присылать callback_query
    # Идентификатор нажатой кнопки (callback_query.data)
    query = update.callback_query
    data = query.data

    if data == constants.CALLBACK_BUTTON_START:
        print("Нажал на START. sub_count стал ", context.chat_data['sub_count'])
        subtheme = tup_subthemes[context.chat_data['sub_count']]
        info = f'<b>{theme}</b>\n\n<i>{subtheme}</i>\n\n{descrp_dict[subtheme]}'
        update.effective_message.reply_html(
            text=info,
            reply_markup=get_start_inline_keyboard(links_dict[subtheme])
        )
        print("Отработал START\n")

    elif data == constants.CALLBACK_BUTTON_NEXT:
        context.chat_data['sub_count'] += 1

        if context.chat_data['sub_count'] > last_index:      # Для того, чтобы счет подтем не выходил
            context.chat_data['sub_count'] = last_index      # за пределы количества подтем (длины кортежа)
        print("Нажал на NEXT. sub_count стал ", context.chat_data['sub_count'])

        subtheme = tup_subthemes[context.chat_data['sub_count']]
        info = f'<b>{theme}</b>\n\n<i>{subtheme}</i>\n\n{descrp_dict[subtheme]}'
        if context.chat_data['sub_count'] < last_index:
            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.HTML,
                reply_markup=get_middle_inline_keyboard(links_dict[subtheme])
            )
        elif context.chat_data['sub_count'] == last_index:

            # Если это тема, которую уже проходил user, то меняем название кнопки "TEST".
            try:
                if context.user_data['level']:
                    query.edit_message_text(
                        text=info,
                        parse_mode=ParseMode.HTML,
                        reply_markup=get_finish_keyboard_changed_theme(links_dict[subtheme])
                    )
                    return
            except KeyError:
                pass

            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.HTML,
                reply_markup=get_finish_inline_keyboard(links_dict[subtheme])
            )
        print("Отработал NEXT\n")

    elif data == constants.CALLBACK_BUTTON_BACK:
        context.chat_data['sub_count'] -= 1

        if context.chat_data['sub_count'] <= 0:      # Для того, чтобы счет подтем не был меньше 0
            context.chat_data['sub_count'] = 0
        print("Нажал на BACK. sub_count стал ", context.chat_data['sub_count'])

        subtheme = tup_subthemes[context.chat_data['sub_count']]
        info = f'<b>{theme}</b>\n\n<i>{subtheme}</i>\n\n{descrp_dict[subtheme]}'
        if context.chat_data['sub_count'] > 0:
            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.HTML,
                reply_markup=get_middle_inline_keyboard(links_dict[subtheme])
            )
        elif context.chat_data['sub_count'] == 0:
            query.edit_message_text(
                text=info,
                parse_mode=ParseMode.HTML,
                reply_markup=get_start_inline_keyboard(links_dict[subtheme])
            )
        print("Отработал BACK \n")

    elif data == constants.CALLBACK_BUTTON_TEST:
        print("Нажал на TEST.")
        # Если это тема, которую уже проходил user, то меняем уровень после её прохождения на тот что был.
        try:
            if context.user_data['level']:
                set_lvl(user_id=user_id, level=context.user_data['level'])
                del context.user_data['level']          # Удаляем level в user_data, потому что уже его вернули обратно
                theme, tup_subthemes, descrp_dict, links_dict = get_info_from_db(user_id=user_id)
                context.chat_data['sub_count'] = 0
                update.effective_message.delete()
                subtheme = tup_subthemes[context.chat_data['sub_count']]
                info = f'<b>{theme}</b>\n\n<i>{subtheme}</i>\n\n{descrp_dict[subtheme]}'

                update.effective_message.reply_html(
                    text=info,
                    reply_markup=get_start_inline_keyboard(links_dict[subtheme])
                )
                return
        except KeyError:
            pass
        # Получаем все вопросы и ответы на них в зависимости от прошедшей темы
        quest_ans, questions, correct_ans = get_tests_from_db(user_id=user_id)
        context.user_data['QUEST_ANS'] = quest_ans
        context.user_data['QUESTIONS'] = questions
        context.user_data['CORRECT_ANS'] = correct_ans
        context.chat_data['sub_count'] = 0       # Обнуляем, чтобы новое открытие тем не было с конца
        context.chat_data['quest_used'] = []
        context.chat_data['quest_count'], ans_var, text = parse.get_test_msg(
            questions=questions,
            quest_ans=quest_ans,
            quest_used=context.chat_data['quest_used'],
            quest_count=context.chat_data['quest_count']
        )
        context.user_data['ANS_VAR'] = ans_var



        update.effective_message.delete()
        update.effective_message.reply_html(
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

    user_id = update.effective_user.id

    ans_var = context.user_data['ANS_VAR']
    questions = context.user_data['QUESTIONS']
    quest_ans = context.user_data['QUEST_ANS']
    correct_ans = context.user_data['CORRECT_ANS']

    if data == constants.CALLBACK_BUTTON_VAR1:
        print("Нажал на VAR1.")

        context.chat_data['quest_count'], context.chat_data['correct_ans_count'], ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=context.chat_data['quest_used'],
            quest_count=context.chat_data['quest_count'],
            correct_ans_count=context.chat_data['correct_ans_count']
        )
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if context.chat_data['quest_count'] == 0:                                # Когда закончились вопросы
            for i in range(len(correct_ans)):               # Для удаления всех ответов пользователя
                query.message.delete()
                update.effective_message.message_id -= 1
            if context.chat_data['correct_ans_count'] == len(correct_ans):       # Если все ответы верны
                inc_lvl(user_id=user_id)
                update.effective_message.reply_html(text=constants.congrat_msg)
                update.effective_message.reply_html(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif context.chat_data['correct_ans_count'] != len(correct_ans):     # Если хоть один ответ не верный
                update.effective_message.reply_html(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(context.chat_data['correct_ans_count']))
            context.chat_data['correct_ans_count'] = 0
            return ConversationHandler.END
        update.effective_message.reply_html(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )

        print("Отработал VAR1 \n")

    elif data == constants.CALLBACK_BUTTON_VAR2:
        print("Нажал на VAR2.")
        context.chat_data['quest_count'], context.chat_data['correct_ans_count'], ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=context.chat_data['quest_used'],
            quest_count=context.chat_data['quest_count'],
            correct_ans_count=context.chat_data['correct_ans_count']
        )
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if context.chat_data['quest_count'] == 0:
            for i in range(len(correct_ans)):
                query.message.delete()
                update.effective_message.message_id -= 1
            if context.chat_data['correct_ans_count'] == len(correct_ans):
                inc_lvl(user_id=user_id)
                update.effective_message.reply_html(text=constants.congrat_msg)
                update.effective_message.reply_html(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif context.chat_data['correct_ans_count'] != len(correct_ans):
                update.effective_message.reply_html(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(context.chat_data['correct_ans_count']))
            context.chat_data['correct_ans_count'] = 0
            return ConversationHandler.END
        update.effective_message.reply_html(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )
        print("Отработал VAR2 \n")

    elif data == constants.CALLBACK_BUTTON_VAR3:
        print("Нажал на VAR3.")
        context.chat_data['quest_count'], context.chat_data['correct_ans_count'], ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=context.chat_data['quest_used'],
            quest_count=context.chat_data['quest_count'],
            correct_ans_count=context.chat_data['correct_ans_count']
        )
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if context.chat_data['quest_count'] == 0:
            for i in range(len(correct_ans)):
                query.message.delete()
                update.effective_message.message_id -= 1
            if context.chat_data['correct_ans_count'] == len(correct_ans):
                inc_lvl(user_id=user_id)
                update.effective_message.reply_html(text=constants.congrat_msg)
                update.effective_message.reply_html(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif context.chat_data['correct_ans_count'] != len(correct_ans):
                update.effective_message.reply_html(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(context.chat_data['correct_ans_count']))
            context.chat_data['correct_ans_count'] = 0
            return ConversationHandler.END
        update.effective_message.reply_html(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )
        print("Отработал VAR3 \n")

    elif data == constants.CALLBACK_BUTTON_VAR4:
        print("Нажал на VAR4.")
        # Проверка ответа пользователя
        context.chat_data['quest_count'], context.chat_data['correct_ans_count'], ans_var, text, text_answer = parse.check_answer(
            button=data,
            ans_var=ans_var,
            correct_ans=correct_ans,
            questions=questions,
            quest_ans=quest_ans,
            quest_used=context.chat_data['quest_used'],
            quest_count=context.chat_data['quest_count'],
            correct_ans_count=context.chat_data['correct_ans_count']
        )
        # Ответ от бота
        query.edit_message_text(
            text=text_answer
        )
        context.user_data['ANS_VAR'] = ans_var
        if context.chat_data['quest_count'] == 0:
            for i in range(len(correct_ans)):
                query.message.delete()
                update.effective_message.message_id -= 1
            if context.chat_data['correct_ans_count'] == len(correct_ans):
                inc_lvl(user_id=user_id)
                update.effective_message.reply_html(text=constants.congrat_msg)
                update.effective_message.reply_html(
                    text=constants.offer_msg,
                    reply_markup=get_button_new_theme()
                )
            elif context.chat_data['correct_ans_count'] != len(correct_ans):
                update.effective_message.reply_html(
                    text=constants.upset_msg,
                    reply_markup=get_button_old_theme()
                )
            print("Conversation --- END. {} прав ответов\n".format(context.chat_data['correct_ans_count']))
            context.chat_data['correct_ans_count'] = 0
            return ConversationHandler.END
        update.effective_message.reply_html(
            text=text,
            reply_markup=get_inline_keyboard_for_tests()
        )
        print("Отработал VAR4 \n")
    print("Conversation --- CONTINUE {}\n".format(context.chat_data['correct_ans_count']))
    return constants.VARS
#  <========================================================================================>


@debug_requests
def start_handler(update: Update, context: CallbackContext):
    """
    Начало работы бота.
    Если юзер был зарегистрирован, то он удаляется с таблицы users.
    """
    # Инициализация переменных в chat_data
    init_global_vars(update=update, context=context)

    user_id = update.effective_user.id
    if get_user_from_db(user_id=user_id) is not None:
        delete_user_from_db(user_id=user_id)
        update.message.reply_html(text=constants.del_user_msg)
    else:
        update.message.reply_html(text=constants.greeting_msg)

    try:        # Если в диалоге, то отменить диалог
        if context.chat_data['in_conv_reg'] or context.chat_data['in_conv_test'] or context.chat_data['in_conv_theme']:
            context.chat_data['in_conv_reg'] = False
            context.chat_data['in_conv_test'] = False
            context.chat_data['in_conv_theme'] = False
            return ConversationHandler.END
    except KeyError:
        pass


@debug_requests
def help_handler(update: Update, context: CallbackContext):
    """
    Описание бота.
    """
    update.message.reply_html(text=constants.help_msg)


@debug_requests
def plan_handler(update: Update, context: CallbackContext):
    """
    Описание тем обучения.
    """
    update.message.reply_html(text=constants.plan_msg)


@debug_requests
def get_lvl_handler(update: Update, context: CallbackContext):
    """
    Получение уровня пользователя.
    """
    lvl = get_lvl(user_id=update.effective_user.id)
    if isinstance(lvl, int):
        update.message.reply_text(text=f"Ваш уровень: {lvl}")
    elif isinstance(lvl, str):
        update.message.reply_text(text=lvl)


@debug_requests
def quiet_handler(update: Update, context: CallbackContext):
    """
    Успокоить пользователя.
    """
    # user_id = update.effective_user.id
    # text = update.effective_message.text
    #
    # if user_id == 357912833:
    #     update.effective_message.bot.send_message(chat_id=429623673, text=text)

    if context.chat_data['flag_upshut'] < 2:
        context.chat_data['flag_upshut'] += 1
    elif context.chat_data['flag_for_del_msg'] < 1:
        update.effective_message.reply_sticker(
            sticker=Sticker(                    # Стикер "Приведение (Чшшш)"
                file_id='CAACAgIAAxkBAAIEa17LHgIb22R-EgkdalwzI327QeVAAAK-AAMw1J0RtKcIkYQmscoZBA',
                file_unique_id='AgADvgADMNSdEQ',
                width=512,
                height=512,
                is_animated=True
            )
        )
        context.chat_data['flag_for_del_msg'] += 1
        context.chat_data['flag_upshut'] = 0
    elif context.chat_data['flag_for_del_msg'] == 1:
        update.effective_message.reply_sticker(
            sticker=Sticker(                    # Стикер "Приведение (Лопает)"
                file_id='CAACAgIAAxkBAAIHbl7Zja1kbyzuuk-pggdbRiFPRHFiAAK8AAMw1J0Rd5meEIvSc6IaBA',
                file_unique_id='AgADvAADMNSdEQ',
                width=512,
                height=512,
                is_animated=True
            )
        )
        context.chat_data['flag_for_del_msg'] += 1
        context.chat_data['flag_upshut'] = 3
    else:
        update.effective_message.delete()


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
    update.message.reply_html(
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
#  <========================================================================================>


#  <============================== Для смены темы в боте ========================================>
@debug_requests
def choose_theme_handler1(update: Update, context: CallbackContext):
    """
    Начало диалога для выбора темы пользователем, которую он проходил.
    (Для повторения, например)
    """
    context.chat_data['in_conv_theme'] = True
    update.message.reply_html(text=constants.choose_theme_msg)
    return constants.THEME


@debug_requests
def choose_theme_handler2(update: Update, context: CallbackContext):
    """
    Выбор темы пользователем, которую он проходил.
    (Для повторения, например)
    """
    user_id = update.effective_user.id
    msg = int(update.effective_message.text)
    lvl = get_lvl(user_id=update.effective_user.id)

    if msg >= lvl:
        update.message.reply_html(text="⛔️⛔️⛔️\n<i>К сожалению, вам не доступна эта тема</i>")
        return constants.THEME
    elif 0 >= msg < 8:
        update.message.reply_html(text="⛔️⛔️⛔️\n<i>Неверно введенный номер темы</i>")
        return constants.THEME
    else:
        context.user_data['level'] = lvl
        set_lvl(user_id=user_id, level=msg)
        context.chat_data['in_conv_theme'] = False
        update.message.reply_html(
            text=f"✅Тема №{msg} выбрана",
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
#  <========================================================================================>

@debug_requests
def cancel_handler(update: Update, context: CallbackContext):
    """
    Отмена всего диалога, данные будут утеряны
    """
    try:
        if context.chat_data['in_conv_reg']:
            update.message.reply_text(text='🚫Отмена.\nДля регистрации с нуля нажмите /reg')
            context.chat_data['in_conv_reg'] = False
    except KeyError:
        pass

    try:
        if context.chat_data['in_conv_test']:
            context.chat_data['quest_count'] = 0
            context.chat_data['correct_ans_count'] = 0
            update.message.reply_html(
                text='🚫Отмена теста.\nПожалуйста, пройдите заново материал.',
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
    except KeyError:
        pass

    try:
        if context.chat_data['in_conv_theme']:
            update.message.reply_html(
                text='🚫Отмена.\n Для продолжения изучения нажмите кнопку.',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text=constants.TITLES[constants.CALLBACK_BUTTON_START],
                                                 callback_data=constants.CALLBACK_BUTTON_START)
                        ],
                    ],
                )
            )
            context.chat_data['in_conv_theme'] = False
    except KeyError:
        pass
    return ConversationHandler.END

# Инициализация глобальных переменных для пользователя
def init_global_vars(update: Update, context: CallbackContext):
    context.chat_data['sub_count'] = constants.sub_count
    context.chat_data['quest_count'] = constants.quest_count
    context.chat_data['quest_used'] = constants.quest_used
    context.chat_data['correct_ans_count'] = constants.correct_ans_count
    context.chat_data['flag_upshut'] = constants.flag_upshut
    context.chat_data['flag_for_del_msg'] = constants.flag_for_del_msg

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

    handler_test = ConversationHandler(
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
    updater.dispatcher.add_handler(handler_test)

    handler_choose_theme = ConversationHandler(
        entry_points=[
            CommandHandler('theme', choose_theme_handler1)
        ],
        states={
            constants.THEME: [
                MessageHandler((Filters.text & (~Filters.command) & Filters.regex(r'^-\d+$|^\d+$')), choose_theme_handler2)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
            CommandHandler('start', start_handler)
        ],
        # per_message=True
    )
    updater.dispatcher.add_handler(handler_choose_theme)

    handler_start = CommandHandler('start', start_handler)
    updater.dispatcher.add_handler(handler_start)

    handler_help = CommandHandler('help', help_handler)
    updater.dispatcher.add_handler(handler_help)

    handler_plan = CommandHandler('plan', plan_handler)
    updater.dispatcher.add_handler(handler_plan)

    handler_lvl = CommandHandler('level', get_lvl_handler)
    updater.dispatcher.add_handler(handler_lvl)

    updater.dispatcher.add_handler(CommandHandler('continue', init_global_vars))

    handler_quiet = MessageHandler(Filters.all, quiet_handler)
    updater.dispatcher.add_handler(handler_quiet)




    # Бесконечная обработка входящих сообщений
    updater.start_polling()
    updater.idle()
    logger.info('Stop EnglishBot')


if __name__ == '__main__':
    main()
