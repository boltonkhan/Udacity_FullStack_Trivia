"""Unittests, integration test of API."""

import json
import os
import random
import re
from string import ascii_letters
import sys
import time
import unittest
from unicodedata import category
from urllib import response

import psycopg2
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc

import init_data
from config import Enviroment, PostgresDbParams
from flaskr import create_app
from models import Category, Question, setup_db


def setup_db_server_conn():
    """Create connection to the db server."""
    master_db = os.environ.get("TRIVIA_MASTER_DATABASE_NAME")
    if not master_db:
        master_db = "postgres"

    params = PostgresDbParams(Enviroment.TEST)
    conn = psycopg2.connect(database=master_db, user=params.username,
                            password=params.password, host=params.host,
                            port=params.port)
    conn.autocommit = True

    return conn


def create_database():
    """Create test database."""
    conn = setup_db_server_conn()
    params = PostgresDbParams(Enviroment.TEST)

    cursor = conn.cursor()

    sql = f"CREATE database {params.database};"
    cursor.execute(sql)

    print("Database created.......")
    conn.close()


def kill_active_connections():
    """Kill active connection."""
    conn = setup_db_server_conn()
    params = PostgresDbParams(Enviroment.TEST)

    cursor = conn.cursor()

    sql = f"""SELECT pg_terminate_backend(pid)
              FROM pg_stat_activity
              WHERE pid <> pg_backend_pid()
              AND pg_stat_activity.datname = '{params.database}';"""
    cursor.execute(sql)

    print("\nConnection killed....")
    conn.close()


def drop_database():
    """Drop test database."""
    conn = setup_db_server_conn()
    params = PostgresDbParams(Enviroment.TEST)

    cursor = conn.cursor()

    sql = f"DROP database {params.database};"
    cursor.execute(sql)

    print("Database dropped....")
    conn.close()


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case."""

    @classmethod
    def setUpClass(cls) -> None:
        """Define test variables and initialize app."""
        app = create_app()
        app.config.from_object('config.TestConfig')
        client = app.test_client()
        db = setup_db(app)

        try:
            create_database()
            # binds the app to the current context
            with app.app_context():
                db.init_app(app)
                db.create_all()

            init_data.run(app)

        except sqlalchemy.exc.OperationalError as e:
            print(f"Connection to the db failed. "
                  f"Details: {e.code}, {e.orig}")

        except psycopg2.OperationalError as e:
            print(f"Connection to the db failed. "
                  f"Details: {e.pgcode}, {e.pgerror}")

        except psycopg2.ProgrammingError as e:
            if e.pgcode == "42P04":  # db exists
                kill_active_connections()
                drop_database()
                cls.setUpClass()

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.app.config.from_object('config.TestConfig')
        self.client = self.app.test_client()
        self.db = setup_db(self.app)

        try:
            # binds the app to the current context
            with self.app.app_context():
                self.db.init_app(self.app)
                self.db.create_all()

        except sqlalchemy.exc.OperationalError as e:
            print(f"Connection to the db failed. "
                  f"Details: {e.code}, {e.orig}")

        except psycopg2.OperationalError as e:
            print(f"Connection to the db failed. "
                  f"Details: {e.pgcode}, {e.pgerror}")

    def tearDown(self):
        """Execute after reach test."""
        super(TriviaTestCase, self).tearDown()

    @classmethod
    def tearDownClass(cls):
        """Clean resources."""
        try:
            drop_database()

        except psycopg2.OperationalError as e:
            if e.pgcode == "55006":  # ObjectInUse
                kill_active_connections()
                cls.tearDownClass()

    # test headers added to all requests
    def test_is_content_json_header(self):
        """Check if content-type header is set up to application/json."""
        response = self.client.get('/api/v1.0/categories')

        content_type = response.headers.get("Content-Type", None)

        self.assertEqual(content_type.lower(), "application/json")

    def test_access_control_allow_origin_set_up(self):
        """Check CORS setup header."""
        response = self.client.get('/api/v1.0/categories')

        content_type = response.headers.get(
            "Access-Control-Allow-Origin", None)

        self.assertEqual(content_type, "*")

    def test_access_control_allow_methods_set_up(self):
        """Check CORS setup for methods header."""
        response = self.client.get('/api/v1.0/categories')

        content_type = response.headers.get(
            "Access-Control-Allow-Methods", None)

        self.assertEqual(content_type.upper(),
                         "GET,PUT,PATCH,POST,DELETE,OPTION")

    # GET /api/v1.0/categories endpoint
    def test_get_all_categories_without_param_success(self):
        """Test success.

        - Status code 200.
        - Count equal in the db and in the response.
        """
        response = self.client.get('/api/v1.0/categories')

        categories = len(Category.get_all())
        res_categories = len(response.json["categories"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(categories, res_categories)

    def test_get_categories_with_emptyIncluded_false_success(self):
        """Test success.

        - Status code 200.
        - Count equal in the db and in the response.
        """
        accepted_vals = ["False", "false"]
        for param in accepted_vals:
            response = self.client.get(
                f"/api/v1.0/categories?emptyIncluded={param}")

            res_categories = response.json["categories"]
            not_empty = True
            for cat in res_categories:
                question = Question.get_by_category_id(cat)
                if cat is None:
                    not_empty = False
                    break

            self.assertEqual(response.status_code, 200)
            self.assertEqual(not_empty, True)

    # GET /api/v1.0/questions endpoint
    def test_get_questions_default_page_success(self):
        """Test success.

        - Status code 200.
        - Db count and response count equal.
        """
        response = self.client.get('/api/v1.0/questions')

        questions = len(Question.get_paginated(1, 10))
        res_questions = len(response.json["questions"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(questions, res_questions)

    def test_get_question_with_query_param_success(self):
        """Test success. Request with a query param.

        - Status code 200.
        - Counts in db and in response are equal .
        """
        response = self.client.get('/api/v1.0/questions?page=2')

        db_questions = len(Question.get_paginated(2, 10))
        res_questions = len(response.get_json()["questions"])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(res_questions, db_questions)

    def test_page_out_of_range(self):
        """Test error: page out of range, status code 404."""
        page_count = int(Question.get_count() / 10)
        response = self.client.get(
            f'/api/v1.0/questions?page={page_count + 3}')

        self.assertEqual(response.status_code, 404)

    # GET /questions/<int:question_id>
    def test_get_question_by_id_request_successed(self):
        """Test success.

        - Status code 200.
        - The same question return from the db and the endpoint.
        """
        questions = Question.get_all()
        question = random.choice(questions)

        response = self.client.get(f"/api/v1.0/questions/{question.id}")
        res_question = response.json["question"]["id"]

        self.assertEqual(question.id, res_question)
        self.assertEqual(response.status_code, 200)

    def test_get_question_error_not_found(self):
        """Test error: question not in the database. Status: 404."""
        questions = Question.get_all()
        db_ids = [q.id for q in questions]
        question_id = None

        while True:
            question_id = random.randint(1, sys.maxsize)
            if question_id not in db_ids:
                break

        response = self.client.get(f"/api/v1.0/questions/{question_id}")

        self.assertEqual(response.status_code, 404)

    # POST /questions
    def test_post_create_question_success(self):
        """Test success: question created.

        - Status: 201.
        - Location header set up.
        - Added question exists in the database.
        """
        categories = Category.get_all()
        category = random.choice(categories)

        response = self.client.post("/api/v1.0/questions", json={
            "question": "Test question",
            "answer": "Test answer",
            "category": category.id,
            "difficulty": 1
        })

        id = response.location.split("/")[-1]
        question = Question.get_by_id(id)

        self.assertIsNotNone(response.location)
        self.assertIsNotNone(question)
        self.assertEqual(response.status_code, 201)

    def test_post_create_question_error_not_valid_body(self):
        """Test error: question not in the database. Status: 400."""
        response = self.client.post("/api/v1.0/questions", json={
            "question": "Test question",
            "answer": "Test answer",
            "category": "text_not_int",
            "difficulty": "1"
        })

        self.assertEqual(response.status_code, 400)

    def test_questions_question_id_not_digestible(self):
        """Test error: not digestable entity."""
        response = self.client.post("/api/v1.0/questions/1", json={
            "key": "value"
        })

        self.assertEqual(response.status_code, 422)

    # DELETE /api/v1.0/questions/<int:question_id>
    def test_delete_question_success(self):
        """Test success: delete question.

        - Status 200.
        - The question doen not exist in the db.
        """
        question = random.choice(Question.get_all())

        response = self.client.delete(f"/api/v1.0/questions/{question.id}")
        del_question = Question.get_by_id(question.id)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(del_question)

    # DELETE /api/v1.0/questions/<int:question_id>
    def test_delete_question_error_resource_not_found(self):
        """Test error: resource not found. Status 404."""
        response = self.client.delete(f"/api/v1.0/questions/fake_id")

        self.assertEqual(response.status_code, 404)

    # POST /api/v1.0/questions/searches
    def test_post_search_successed(self):
        """Test success: questions found.

        - Status code: 200.
        - All questions contains searching term.
        """
        search_term = "what"
        response = self.client.post("/api/v1.0/questions/searches", json={
            "searchTerm": search_term
        })

        for question in response.json["questions"]:
            self.assertRegex(question["question"].lower(), ".*what.*")
        self.assertEqual(response.status_code, 200)

    def test_post_search_searchTerm_body_parameter_not_found(self):
        """Test error: searchTerm not found in the post body. Status 400."""
        response = self.client.post("/api/v1.0/questions/searches", json={
            "key": "value"
        })

        self.assertEqual(response.status_code, 400)

    def test_post_search_return_empty_list(self):
        """Test success: search not found.

        - Status code 200.
        - Empty list returned.
        """
        random_ascii = ''.join(random.choices(ascii_letters, k=30))
        search_term = random_ascii

        response = self.client.post("/api/v1.0/questions/searches", json={
            "searchTerm": search_term
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["questions"], [])

    # GET "/api/v1.0/categories/<int:category_id>/questions"
    def test_get_questions_from_the_category_success(self):
        """Test success: take all questions for the provided category id.

        - Status code 200.
        - Question Count are the same in db and from the endpoint.
        """
        cat_ids = [c.id for c in Category.get_all()]
        category_id = None

        for cat_id in cat_ids:
            questions = Question.get_by_category_id(cat_id)
            category_id = cat_id

            if questions:
                break

        response = self.client.get(
            f"/api/v1.0/categories/{category_id}/questions")

        self.assertEqual(len(response.json["questions"]), len(questions))

    def test_get_questions_from_the_category_error_not_found(self):
        """Test error: there is no category with a given id in the db.

        - Status code: 404.
        """
        db_ids = [q.id for q in Category.get_all()]
        category_id = None

        while True:
            category_id = random.randint(1, sys.maxsize)
            if category_id not in db_ids:
                break

        response = self.client.get(
            f"/api/v1.0/categories/{category_id}/questions")

        self.assertEqual(response.status_code, 404)

    # POST /api/v1.0/quizzes
    def test_quizzes_success_response(self):
        """Test success: status code 200."""
        categories = Category.get_all()
        category = None

        for cat in categories:
            questions = Question.get_by_category_id(cat.id)

            if questions:
                category = cat
                break

        category = category.format()

        response = self.client.post("/api/v1.0/quizzes", json={
            "previous_questions": [],
            "quiz_category": category
        })

        self.assertEqual(response.status_code, 200)

    def test_quizzes_success_previous_question_not_include(self):
        """Test success.

        - Status code 200
        - Returned question is not in a list of previos questions.
        """
        categories = Category.get_all()
        category = None
        previous_questions = []

        for cat in categories:
            questions = Question.get_by_category_id(cat.id)

            if len(questions) > 1:
                questions = random.choices(questions, k=1)
                previous_questions = [q.id for q in questions]
                category = cat
                break

        category = category.format()

        response = self.client.post("/api/v1.0/quizzes", json={
            "previous_questions": previous_questions,
            "quiz_category": category
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(response.json["question"], previous_questions)

    def test_quizzes_error_catagory_not_found(self):
        """Test error: category out of range."""
        db_ids = [q.id for q in Category.get_all()]
        category_id = None

        while True:
            category_id = random.randint(1, sys.maxsize)
            if category_id not in db_ids:
                break

        response = self.client.post("/api/v1.0/quizzes", json={
            "previous_questions": [],
            "quiz_category": {
                "type": "test_type",
                "id": category_id
            }
        })

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
