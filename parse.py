import random
import constants
from typing import Tuple



def get_test_msg(questions: list, quest_used: list, quest_ans: dict, quest_count: int) -> Tuple[int, tuple, str]:
    quest = random.choice(questions)
    quest_not_used = list(set(questions) - set(quest_used))     # Неиспользованные вопросы

    if quest not in quest_used and quest_not_used != []:
        # Если вопроса нет в списке использованных вопросов и неисп. вопросы еще есть
        quest_used.append(quest)            # то добавляем вопрос в список использованных
        quest_count += 1
        random.shuffle(quest_ans[quest])    # Перемешиваем варианты ответов
        ans_var = quest_ans[quest]
        text = f"""
            _Вопрос {quest_count}_

*{quest}*

1) {ans_var[0]}
2) {ans_var[1]}
3) {ans_var[2]}
4) {ans_var[3]}
                    """
        return quest_count, ans_var, text

    elif quest in quest_used and quest_not_used != []:
        # Если вопрос в списке использованных, а неисп. вопросы еще есть, то рекурсия этой функции
        return get_test_msg(
            questions=quest_not_used,   # передаем неиспользованные вопросы в рекурсивную функцию
            quest_used=quest_used,
            quest_ans=quest_ans,
            quest_count=quest_count
        )

    elif quest_not_used == []:
        quest_count = 0
        ans_var = ('', '', '', '')
        text = "Вопросы закончились"
        return quest_count, ans_var, text


def check_answer(button: str, ans_var: tuple, correct_ans: tuple, questions: list,
                 quest_ans: dict, quest_used: list, quest_count: int, correct_ans_count: int) -> Tuple[int, int, tuple, str, str]:
    button = int(button)
    if ans_var[button] in correct_ans:
        correct_ans_count += 1
        quest_count, ans_var, text = get_test_msg(
            questions=questions,
            quest_ans=quest_ans,
            quest_used=quest_used,
            quest_count=quest_count
        )
        return quest_count, correct_ans_count, ans_var, text, constants.correct_answer
    elif ans_var[button] not in correct_ans:
        quest_count, ans_var, text = get_test_msg(
            questions=questions,
            quest_ans=quest_ans,
            quest_used=quest_used,
            quest_count=quest_count
        )
        return quest_count, correct_ans_count, ans_var, text, constants.wrong_answer


