import psycopg
import pytest


@pytest.fixture
def db():
    connection = psycopg.connect("dbname=snapshift_test")
    yield connection
    connection.rollback()
    connection.close()
