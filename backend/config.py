"""Module with Flask configurations."""

import os
from enum import Enum


basedir = os.path.abspath(os.path.dirname(__file__))


class Enviroment(Enum):
    """Enum represents the enviroment."""

    PROD = 1
    TEST = 2


class PostgresDbParams:
    """Create db connection parameters."""

    def __init__(self, enviroment: Enviroment):
        """Create a db config."""
        if enviroment in Enviroment:

            if enviroment == Enviroment.TEST:

                self.username = os.environ.get("TRIVIA_DB_USERNAME_TEST")
                self.password = os.environ.get("TRIVIA_DB_PASSWORD_TEST")

                self.host = os.environ.get("TRIVIA_DB_HOST_TEST")
                if not self.host:
                    self.host = "localhost"

                self.port = os.environ.get("TRIVIA_DB_PORT_TEST")
                if not self.port:
                    self.port = 5432

                self.database = os.environ.get("TRIVIA_DB_NAME_TEST")
                if not self.database:
                    self.database = "trivia_test"

        if enviroment == Enviroment.PROD:

            self.username = os.environ.get("TRIVIA_DB_USERNAME_PROD")
            self.password = os.environ.get("TRIVIA_DB_PASSWORD_PROD")

            self.host = os.environ.get("TRIVIA_DB_HOST_PROD")
            if not self.host:
                self.host = "localhost"

            self.port = os.environ.get("TRIVIA_DB_PORT_PROD")
            if not self.port:
                self.port = 5432

            self.database = os.environ.get("TRIVIA_DB_NAME_PROD")
            if not self.database:
                self.database = "trivia_app"

        self.conn_str = f"postgresql://"                    \
                        f"{self.username}:{self.password}"  \
                        f"@{self.host}:{self.port}"         \
                        f"/{self.database}"


class Config:
    """Configuration of the flask app for a production."""

    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = PostgresDbParams(Enviroment.PROD).conn_str
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(Config):
    """Configuration of the flask app for a test env."""

    SQLALCHEMY_DATABASE_URI = PostgresDbParams(Enviroment.TEST).conn_str
    SQLALCHEMY_TRACK_MODIFICATIONS = False
