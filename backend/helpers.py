"""Additional tools used in api endpoints."""

import os
import json
from unicodedata import category

from models import Question
from typing import List


def is_valid_question(data: json) -> bool:
    """Check if body request (POST questions/) is valid.

    :param data: request data
    :data type: dict
    :rtype: bool
    """
    question_text = data.get("question", None)
    answer = data.get("answer", None)
    difficulty = data.get("difficulty", None)
    category = data.get("category", None)

    if not question_text or not answer or not difficulty or not category:
        return False

    try:
        difficulty = int(difficulty)
        category = int(category)

        if difficulty <= 0 or difficulty > 5 or category <= 0:
            raise ValueError

    except ValueError:
        return False

    return True


def is_valid_quize_data(data: json) -> bool:
    """Check if body request (POST /quizes) is valid.

    :param data: request data
    :data type: dict
    :rtype: bool
    """
    prev_questions = data.get("previous_questions", None)
    category = data.get("quiz_category", None)

    if prev_questions is None or category is None:
        return False

    if not isinstance(prev_questions, list):
        return False

    category_id = category.get("id", None)
    category_type = category.get("type", None)

    if category_id is None or category_type is None:
        return False

    try:
        int(category_id)
        if prev_questions:
            for question in prev_questions:
                int(question)

    except ValueError:
        return False

    return True


def filter_categories_without_questions(
        categories: dict, questions: List[Question]):
    """Filter categories with no questions.

    :param categories: a collection to filter
    :category type: dict
    :param questions: a collection to use as filter
    :questions type: `List[Question]`
    """
    ids = [q.category_id for q in questions]

    return {k: v for k, v in categories.items() if int(k) in ids}
