import random
from typing import Tuple


def make_msg(theme: str, subtheme: str, descrp: str):
    theme = '*' + theme + '*'
    subtheme = '_' + subtheme + '_'
    msg = '\n\n'.join([theme, subtheme, descrp])
    return msg


def get_test_msg(questions: list, quest_used: list, quest_ans: dict, quest_count: int) -> Tuple[str, tuple, int]:
    quest = random.choice(questions)

    if quest not in quest_used and quest_count != len(questions):  # Если вопроса нет в списке использованных вопросов и вопросы не закончились
        quest_used.append(quest)            # то добавляем вопрос в список
        quest_count += 1
        random.shuffle(quest_ans[quest])    # Перемешиваем варианты ответов
        ans_var = quest_ans[quest]
        return quest, ans_var, quest_count

    # elif quest in quest_used and quest_count != len(questions):  # Если вопрос в списке и вопросы не закончились, то
    #     # рекурсия этой функции
    #     get_test_msg(questions=questions, quest_used=quest_used, quest_ans=quest_ans, quest_count=quest_count)

    elif quest_count > len(questions):
        quest = ''
        ans_var = tuple()
        quest_count = 0
        return quest, ans_var, quest_count
