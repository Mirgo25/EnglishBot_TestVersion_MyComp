NAME, SURNAME = range(2)
VARS = 'VARS'

greeting_msg = """
*Привет! Я English Bot.* 🇬🇧
Научу тебя грамматики английского языка.
Но сперва тебе нужно зарегистрироваться с помощью команды /reg.

_Чтобы посмотреть дополнительную информацию, введите команду_ /help
"""

help_msg = """
Когда вы зарегистрируетесь в боте, у вас будет уровень 1.🚩
Один уровень - одна тема.✅
Чем больше уровень, тем больше тем вы сможете изучить.😉

*Команды:*
`Команда` /start - Перезапустить бота (при этом обнулится ваш уровень и всё обучение начнётся сначала).
`Команда` /help - Дополнительная информация о боте.
`Команда` /reg - Зарегистрироваться в боте.
`Команда` /plan - Темы обучения грамматике.
"""

plan_msg = """
1. *Noun* - Имя существительное _(число, исчисляемые / неисчисляемые сущ., притяжательный падеж, артикли)_.

2. *Pronoun* - Местоимение _(личные, притяжательные, абсолютные притяжательные, возвратные, указательные, неопределенные местоимения)_.

3. *Adjective* and *Adverb* - Прилагательное и наречие _(степени сравнения прилагательных и наречий)_.

4. *Number* - Числительное _(количественные и порядковые)_.

5. *Verb* - Глагол _(времена, правильные / неправильные глаголы, страдательный залог, модальные глаголы, косвенная речь, условные предложения, инфинитив, герундий, причастие I и II)_.

6. *Prepositions and phrasal verbs* - Предлоги и фразовые глаголы.

7. *Sentence* - Предложение _(типы предложений, порядок слов в предложении)_.
"""

after_reg_msg = """
Рекомендую ознакомиться с планом обучения, если вы еще не видели его 😜
_Для этого нажмите команду_ /plan

Если вы уже ознакомлены с ним, то *LET'S STUDY!*
"""

del_user_msg = """
Вы были удалены.
Зарегистрируйетсь, пожалуйста, заново, с помощью команды /reg"""

reg_msg = """
Вы еще не зарегистрированы.
Зарегистрируйетсь, пожалуйста, с помощью команды /reg"""

correct_answer = "Правильно✅"
wrong_answer = "Неправильно❌"

# Идентификаторы кнопок
CALLBACK_BUTTON_START = 'callback_button_start'
CALLBACK_BUTTON_LINK = 'callback_button_link'
CALLBACK_BUTTON_NEXT = 'callback_button_next'
CALLBACK_BUTTON_BACK = 'callback_button_back'
CALLBACK_BUTTON_TEST = 'callback_button_test'
CALLBACK_BUTTON_VAR1 = 'callback_button_var1'
CALLBACK_BUTTON_VAR2 = 'callback_button_var2'
CALLBACK_BUTTON_VAR3 = 'callback_button_var3'
CALLBACK_BUTTON_VAR4 = 'callback_button_var4'


# Названия кнопок
TITLES = {
    CALLBACK_BUTTON_START: "✌LET'S GET STARTED!!!✌",
    CALLBACK_BUTTON_LINK: "Подробнее🔍",
    CALLBACK_BUTTON_NEXT: "Next➡",
    CALLBACK_BUTTON_BACK: "Back⬅️",
    CALLBACK_BUTTON_TEST: "❓TEST❓",
    CALLBACK_BUTTON_VAR1: "1️⃣",
    CALLBACK_BUTTON_VAR2: "2️⃣",
    CALLBACK_BUTTON_VAR3: "3️⃣",
    CALLBACK_BUTTON_VAR4: "4️⃣",

}
