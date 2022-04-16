"""Database models and interfaces to operate on them."""

import os
from flask import session
from numpy import delete
from sqlalchemy import Column, String, Integer, func
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json


db = SQLAlchemy()


def setup_db(app):
    """Binds a flask application and a SQLAlchemy service."""
    db.app = app
    db.init_app(app)
    Migrate(app, db)
    return db


class Category(db.Model):
    """Represent Category object in a database.

    :param id: identification number in a database
    :id type: Integer
    :param type: label of the category
    :type type: int
    """

    __tablename__ = 'categories'

    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String(), nullable=False)
    questions = db.relationship('Question', backref="question")

    def __init__(self, type: str):
        """Create an object."""
        self.type = type

    def insert(self):
        """Insert new object to the db."""
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self

    def delete(self):
        """Remove the object from db."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all(cls):
        """Get all categories."""
        return Category.query.all()

    @classmethod
    def get_by_id(cls, category_id: int):
        """Return category by id.

        :param category_id: category id
        :category_id type: int
        """
        return Category.query.get(category_id)

    def format(self):
        """Return the object in format easy to serialize with json."""
        return {
            'id': self.id,
            'type': self.type
            }

    @classmethod
    def all_as_dict(cls):
        """Return all categories as a dict."""
        cat_dict = {}
        all_cat = Category.query.all()
        for cat in all_cat:
            cat_dict[f"{cat.id}"] = cat.type
        return cat_dict


class Question(db.Model):
    """Represent Question object in a database.

    :param id: identification number in a database
    :id type: Integer
    :param category_id: id of category of the question
    :category_id type: int
    :param question_text: the question
    :question_text type: str
    :param answer: the answer to the question
    :answer type: str
    :param difficulty: the level of difficulty of the question
    :dufficulty type: int
    """

    __tablename__ = 'questions'

    id = Column(db.Integer(), primary_key=True)
    category_id = \
        db.Column(
            db.Integer, db.ForeignKey('categories.id'), nullable=False)
    question_text = Column(db.String(), nullable=False)
    answer = Column(db.String, nullable=False)
    difficulty = Column(db.Integer(), nullable=False)

    def __init__(self, question: str, answer: str,
                 category_id: int, difficulty: int):
        """Create an object."""
        self.question_text = question
        self.answer = answer
        self.category_id = category_id
        self.difficulty = difficulty

    def __eq__(self, other):
        """Compare objects.

        :param other: object to compare
        :other type: `Question`
        """
        if isinstance(other, Question):
            return self.id == other.id

        return False

    def insert(self):
        """Create a new object in the db."""
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        return self

    def update(self):
        """Update an existing object."""
        db.session.commit()

    def delete(self):
        """Delete an existing object from the db."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, question_id: int):
        """Return question object.

        :param question_id: identificator of the question
        :question_id type: int
        """
        return Question.query.get(question_id)

    @classmethod
    def get_all(cls):
        """Return all questions from the db."""
        return Question.query.all()

    @classmethod
    def get_by_category_id(cls, category_id: int):
        """Return questions for a given categry.

        :param category_id: id of category
        :category_id type: int
        """
        return Question.query.filter(Question.category_id == category_id).all()

    @classmethod
    def get_count(cls):
        """Return a count of all objects in db."""
        return db.session.query(func.count(Question.id)).scalar()

    @classmethod
    def get_paginated(cls, page: int, page_size: int):
        """Return paginated questions.

        :param page: page number
        :page type: int
        :param page_size: number of items to return
        :page_size type: int
        """
        return Question.query.limit(page_size) \
                       .offset((page - 1) * page_size).all()

    @classmethod
    def search(cls, search_term: str):
        """Search question.

        :param search_term: term to search in question
        :search_term type: str
        """
        return Question.query.filter(
            func.lower(
                Question.question_text).contains(search_term.lower())).all()

    def format(self):
        """Return the object in format easy to serialize with json."""
        return {
            'id': self.id,
            'question': self.question_text,
            'answer': self.answer,
            'category': self.category_id,
            'difficulty': self.difficulty
            }
