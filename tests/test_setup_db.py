import pytest
import psycopg2
from database.setup_db import create_database_and_user


POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "pass"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
NEW_DATABASE = "banking_db"
NEW_USER = "banking_user"


@pytest.fixture(scope="module")
def postgres_connection():
    """Fixture to provide a connection to the PostgreSQL instance."""
    connection = psycopg2.connect(
        dbname="postgres",
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
        port=POSTGRES_PORT
    )
    connection.autocommit = True
    yield connection
    connection.close()


def test_database_exists(postgres_connection):
    """Verify the database exists."""
    cursor = postgres_connection.cursor()
    cursor.execute("SELECT 1 FROM pg_database \
                   WHERE datname = %s;", (NEW_DATABASE,))
    assert cursor.fetchone() is not None, \
        f"Database '{NEW_DATABASE}' does not exist."
    cursor.close()


def test_user_exists(postgres_connection):
    """Verify the user exists."""
    cursor = postgres_connection.cursor()
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s;", (NEW_USER,))
    assert cursor.fetchone() is not None, f"User '{NEW_USER}' does not exist."
    cursor.close()


def test_create_database_and_user():
    """
    Test that the database and user
    creation function runs without errors.
    """
    create_database_and_user()
