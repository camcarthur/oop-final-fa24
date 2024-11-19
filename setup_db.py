import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

""" default user after installing postgres is "postgres"
    password was not working for me so i had to reset to "pass" using the postgres shell
    sudo -u postgres psql
    ALTER USER postgres WITH PASSWORD 'pass'; """
    
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "pass"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432

# Database and user details
NEW_DATABASE = "banking_db"
NEW_USER = "banking_user"
NEW_PASSWORD = "secure_password"

def create_database_and_user():
    try:
        # Connect to PostgreSQL as superuser
        connection = psycopg2.connect(
            dbname="postgres",
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = connection.cursor()

        # Check if the database exists and drop it
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{NEW_DATABASE}';")
        if cursor.fetchone():
            cursor.execute(f"DROP DATABASE {NEW_DATABASE};")
            print(f"Database '{NEW_DATABASE}' dropped successfully.")

        # Create the new database
        cursor.execute(f"CREATE DATABASE {NEW_DATABASE};")
        print(f"Database '{NEW_DATABASE}' created successfully.")

        # Check if the user exists and drop it
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{NEW_USER}';")
        if cursor.fetchone():
            cursor.execute(f"DROP ROLE {NEW_USER};")
            print(f"User '{NEW_USER}' dropped successfully.")

        # Create the new user
        cursor.execute(f"CREATE USER {NEW_USER} WITH PASSWORD '{NEW_PASSWORD}';")
        print(f"User '{NEW_USER}' created successfully.")

        # Grant privileges to the new user on the new database
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {NEW_DATABASE} TO {NEW_USER};")
        print(f"Granted privileges on database '{NEW_DATABASE}' to user '{NEW_USER}'.")

        # Close the connection
        cursor.close()
        connection.close()

    except psycopg2.Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_database_and_user()
