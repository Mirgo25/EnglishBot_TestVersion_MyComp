import random
from typing import Tuple


def make_msg(theme: str, subtheme: str, descrp: str):
    theme = '*' + theme + '*'
    subtheme = '_' + subtheme + '_'
    msg = '\n\n'.join([theme, subtheme, descrp])
    return msg

def make_mes(quest_count: int, quest: str, ans_var: tuple):
    return f"""
            _Вопрос {quest_count}_

    *{quest}*

    1) {ans_var[0]}
    2) {ans_var[1]}
    3) {ans_var[2]}
    4) {ans_var[3]}
                    """


def get_test_msg(questions: list, quest_used: list, quest_ans: dict, quest_count: int) -> Tuple[int, str, tuple]:
    quest = random.choice(questions)
    quest_not_used = list(set(questions) - set(quest_used))     # Неиспользованные вопросы

    if quest not in quest_used and quest_not_used != []:
        # Если вопроса нет в списке использованных вопросов и неисп. вопросы еще есть
        quest_used.append(quest)            # то добавляем вопрос в список использованных
        quest_count += 1
        random.shuffle(quest_ans[quest])    # Перемешиваем варианты ответов
        ans_var = quest_ans[quest]
        return quest_count, quest, ans_var

    elif quest in quest_used and quest_not_used != []:
        # Если вопрос в списке использованных, а неисп. вопросы еще есть, то рекурсия этой функции
        return get_test_msg(
            questions=quest_not_used,   # передаем неиспользованные вопросы в рекурсивную функцию
            quest_used=quest_used,
            quest_ans=quest_ans,
            quest_count=quest_count
        )

    elif quest_not_used == []:
        quest = ''
        ans_var = ('', '', '', '')
        quest_count = 0
        return quest_count, quest, ans_var
