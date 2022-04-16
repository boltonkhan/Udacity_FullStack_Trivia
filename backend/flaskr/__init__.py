"""Backend of trivia game built as a api."""

from asyncio.log import logger
import json
import logging
import os
import sys
import random
from distutils.log import debug
from unicodedata import category
from urllib import response

import helpers as help
import werkzeug
from flask import Flask, abort, jsonify, make_response, request, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import Category, Question, setup_db
from sqlalchemy import exc
from werkzeug import exceptions as werk_ex
from logging.handlers import TimedRotatingFileHandler


QUESTIONS_PER_PAGE = 10


def create_app():
    """Create and configure the app."""
    logging.basicConfig(filename='err_record.log', level=logging.WARNING,
                        format=f"%(asctime)s %(levelname)s "
                               f"%(name)s %(threadName)s "
                               f"%(lineno)d %(funcName)s : %(message)s"
                        )

    app = Flask(__name__)
    app.config.from_object('config.Config')
    db = setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        """Add headers to the response."""
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = \
            "GET,PUT,PATCH,POST,DELETE,OPTION"
        response.headers["Content-Type"] = "application/json"

        return response

    @app.route('/api/v1.0/categories', methods=['GET'])
    def get_categories():
        """Get categories.

        :param emptyIncluded: query param, True: return all categories,
            False: return only categories with some questions
        :param type: bool, optional, default True
        """
        categories = Category.all_as_dict()
        questions = Question.get_all()

        empty_incl = str(request.args.get("emptyIncluded", None))

        def is_empty_included(empty_incl):
            values = ["True", "False"]
            if empty_incl:
                empty_incl = empty_incl.capitalize()
                if empty_incl in values:
                    return eval(empty_incl)

            return True

        empty_included = is_empty_included(empty_incl)

        if empty_included:
            categories = Category.all_as_dict()

        if not empty_included:
            categories = help. \
                filter_categories_without_questions(categories, questions)

        if not categories:
            raise werk_ex.NotFound("`Categories` not found.")

        return jsonify({
            "success": True,
            "categories": categories
        })

    @app.route('/api/v1.0/questions', methods=["GET"])
    def get_questions():
        """Return all questions, paginated.

        :param page: query param provide as url parameter,
            page from returned questions will be returned,
            page size is 10, optional
        :page type: int, default 1
        """
        page = request.args.get("page", 1, type=int)
        questions = Question.get_paginated(page, QUESTIONS_PER_PAGE)

        if not questions:
            # if not existed, return 404
            raise werk_ex.NotFound("`Questions` not found. "
                                   "Requested page does not exist?")

        total = Question.get_count()
        categories = Category.all_as_dict()
        categories = \
            help.filter_categories_without_questions(categories, questions)

        questions = [question.format() for question
                     in questions]

        return jsonify({
            'success': True,
            'total_questions': total,
            'questions': questions,
            'current_category': None,
            'categories': categories
        })

    @app.route("/api/v1.0/questions/<int:question_id>", methods=["DELETE", "GET"])
    def get_delete_question(question_id: int):
        """As DELETE method: delete a question from database.

        As GET method: return question with a given id
        :param question_id: id of the question to delete or to return
        :question_id type: int
        """
        if request.method == "DELETE":

            question = Question.get_by_id(question_id)

            # if not found return 404 with a message
            if not question:
                raise werk_ex.NotFound(
                    "Requested `Question` doesn not exists.")

            question.delete()

            return jsonify({
                "success": True,
                "message": f"`Question` id: {question_id} "
                           f"has been deleted."
            })

        if request.method == "GET":
            question = Question.get_by_id(question_id)

            # if not found return 404 with a message
            if not question:
                raise werk_ex.NotFound(
                    "Requested `Question` doesn not exists.")

            question = question.format()

            response = jsonify({
                "success": True,
                "question": question
            })

            return response

        raise werk_ex.MethodNotAllowed(f"{request.method} is not allowed.")

    @app.route('/api/v1.0/questions', methods=['POST'])
    def create_question():
        """Create a new question in a database.

        In body:
        :param question: text of the question
        :question type: str
        :param answer: text of the answer
        :answer type: str
        :param category: id of the question category
        :category type: int, accepted only existing in a db values
        :param difficulty: level of difficulty of the question
        :dufficylty type: int, accepted values: 1-5
        """
        try:
            data = request.data.decode('utf8')
            data = json.loads(data)

        # can deserialize body: 400
        except json.JSONDecodeError:
            raise werk_ex.BadRequest("Can not deseriaze json.")

        # can't parse request as a valid question: 400
        if not help.is_valid_question(data):
            raise werk_ex.BadRequest('Wrong format of the `Question` object')

        # category not found: 404
        if not Category.get_by_id(data.get("category")):
            raise werk_ex.BadRequest('Given category doesn not exist.')

        def map_to_question(data: json):
            return Question(
                question=data.get("question"),
                answer=data.get("answer"),
                category_id=data.get("category"),
                difficulty=data.get("difficulty")
            )

        question = map_to_question(data)
        question = question.insert()

        body = jsonify({
            "success": True,
            "message": "Question has been created."
            })

        response = make_response(body)
        location = url_for(
                           'get_delete_question',
                           question_id=question.id,
                           _external=True
                           )
        response.location = location

        return response, 201

    @app.route('/api/v1.0/questions/searches', methods=['POST'])
    def search():
        """Get questions by search term.

        Method is looking for a term in question text. Body parameters:
        :param searchTerm: term to search
        :searchTerm type: str
        """
        try:
            data = request.data.decode('utf8')
            data = json.loads(data)

        # can't deserialize requst body: 400
        except json.JSONDecodeError:
            raise werk_ex.BadRequest("Can not deseriaze json.")

        search_term = data.get("searchTerm", None)

        # no proper parameter in the request body: 400
        if not search_term:
            raise werk_ex.BadRequestKeyError(
                "Required key `searchTerm` is not found.")

        questions = [q.format() for q in Question.search(search_term)]
        total_questions = len(questions)

        response = jsonify({
            "success": True,
            "total_questions": total_questions,
            "questions": questions,
            "current_category": None
        })

        return response

    @app.route("/api/v1.0/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_id(category_id: int):
        """Return all questions for a category.

        :param category_id: id of the category to return question from
        :category_id type: int
        :return: a collection of `Questions`,
            total number of returned questions and current `Category`
        """
        category = Category.get_by_id(category_id)

        # category not found: 404
        if not category:
            raise werk_ex.NotFound("Category not found.")

        questions = Question.get_by_category_id(category_id)

        # questions not found: 404
        if not questions:
            raise werk_ex.NotFound(
                "No questions for a given category found.")

        total_questions = len(questions)
        category = category.format()
        questions_f = [q.format() for q in questions]

        response = jsonify({
            "success": True,
            "total_questions": total_questions,
            "questions": questions_f,
            "current_category": category
        })

        return response, 200

    @app.route("/api/v1.0/quizzes", methods=["POST"])
    def create_quize():
        """Return random question for specified criteria.

        Exclude from searching questions specified by previous_questions
        parameter. Body parameters.
        :param previous_questions: questions to exlude represent by ids
        :previous_questions type: a list of ints
        :param quiz_category: a category to take question from,
            if 0 is provided as category.id question from all categories
            is draw
        :previous_questions type: `Category`
        """
        try:
            data = request.data.decode('utf8')
            data = json.loads(data)

        # can't deserialize data: 400
        except json.JSONDecodeError:
            raise werk_ex.BadRequest("Can not deseriaze json.")

        # data are not valid: 400
        if not help.is_valid_quize_data(data):
            raise werk_ex.BadRequest("Wrong data format.")

        category_id = data.get("quiz_category").get("id")

        questions = []
        if category_id == 0:
            questions = Question.get_all()

        else:
            is_category = Category.get_by_id(category_id)

            # no such category is the database: 404
            if is_category is None:
                raise werk_ex.NotFound("Category not found.")

            else:
                questions = Question.get_by_category_id(category_id)

        prev_question = data.get("previous_question")
        if prev_question:
            questions = \
                [q for q in questions if q.id not in prev_question]

        # no question with specified criteria: 404
        if len(questions) == 0:
            raise werk_ex.NotFound(
                "No questions with specified criteria found.")

        ran_question = random.choice(questions)
        ran_question = ran_question.format()

        return jsonify({
            "success": True,
            "question": ran_question
        })

    @app.errorhandler(werk_ex.NotFound)
    def resource_not_found(error):
        """Resource not found error handler."""
        logger.error(error)
        response = jsonify({
            "success": False,
            "error_code": 404,
            "error_message": error.description
        })

        return response, 404

    @app.errorhandler(422)
    def unprocessable_entity(error):
        logger.error(error)
        response = jsonify({
            "success": False,
            "error_code": 422,
            "error_message": "Unprocessable entity."
        })

        return response, 422

    @app.errorhandler(werk_ex.MethodNotAllowed)
    def method_not_allowed(error):
        logger.error(error)
        response = jsonify({
            "success": False,
            "error_code": 405,
            "error_message": error.description
        })

        return response, 422

    @app.errorhandler(werk_ex.BadRequest)
    def bad_request(error):
        logger.error(error)
        response = jsonify({
            "success": False,
            "error_code": 400,
            "error_message": error.description
        })

        return response, 400

    @app.errorhandler(Exception)
    def unexpected_error(error):
        logger.error(error)
        response = jsonify({
            "success": False,
            "error_code": 500,
            "error_message": "Unexpected error occured."
        })

        return response, 500

    return app
