"""Create sample data for the application."""

import inspect
import pathlib
from typing import List

import pandas as pd
import psycopg2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

from flaskr import create_app
from models import Category, Question, setup_db

CATEGORIES_PATH = pathlib.Path("backend/sample_data/categories.csv")
QUESTIONS_PATH = pathlib.Path("backend/sample_data/questions.csv")


def create_app_context(app=None) -> Flask:
    """Return app context."""
    if app is None:
        app = create_app()
        app.app_context().push()
        return app
    else:
        return app


def get_categories() -> List[Category]:
    """Create category collection based on file data."""
    file_path = CATEGORIES_PATH
    categories = []
    data = pd.read_csv(CATEGORIES_PATH)

    def row_to_category(row):
        if row.Type:
            return Category(type=row.Type)
        return None

    categories = list(map(row_to_category, data.itertuples()))
    return [c for c in categories if c is not None]


def get_questions() -> List[Question]:
    """Create question collection based on file data."""
    file_path = QUESTIONS_PATH
    data = pd.read_csv(QUESTIONS_PATH)

    def row_to_question(row):
        question = row.Question
        answer = row.Answer
        difficulty = row.Difficulty
        category_id = row.Category
        if question and answer and difficulty and category_id:
            try:
                difficulty = int(difficulty)
                category_id = int(category_id)
            except ValueError:
                return None
            else:
                return Question(
                    question=question,
                    answer=answer,
                    difficulty=difficulty,
                    category_id=category_id
                )

    questions = list(map(row_to_question, data.itertuples()))
    return [q for q in questions if q is not None]


def insert_categories(categories: List[Category]) -> None:
    """Insert categories to the db.

    :param categories: a collection of Category objects
    :categories type: `List[Category]`
    """
    for cat in categories:
        cat.insert()


def insert_questions(questions):
    """Insert questions to the db.

    :param questions a collection of Category objects
    :questions type: `List[Question]`
    """
    for question in questions:
        question.insert()


def delete_categories():
    """Delete all categories from the db.

    Has to be add to run() funtion.
    Needs app_context to be pushed.
    """
    cats = Category.get_all()
    for cat in cats:
        cat.delete()


def delete_questions():
    """Delete all questions from the db.

    Has to be add to run() funtion.
    Needs app_context to be pushed.
    """
    questions = Question.get_all()
    for question in questions:
        question.delete()


def run(app=None) -> None:
    """Combine all together.

    Insert categories and questions into the db.
    """
    app = create_app_context(app)
    db = setup_db(app)

    categories = get_categories()
    questions = get_questions()

    try:
        insert_categories(categories)
        insert_questions(questions)

    except AttributeError as e:
        if str(e).find("scoped_session").count > 0:
            print("Session issue?")

    except BaseException as e:
        print(f"Something went wrong! Details: {e}")

    else:
        print("Data loaded......")


if __name__ == "__main__":
    run()
