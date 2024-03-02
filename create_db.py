# prerequisites - set up pg users properly = examples with pepa
# CREATE USER pepa WITH PASSWORD 'pepa';
# ALTER USER pepa WITH createdb;

# check user and roles - pepa should be there with proper grants & password
# SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb, rolcanlogin  FROM pg_roles;
# SELECT rolname AS username, rolpassword AS password_hash FROM pg_authid;


import psycopg2
from psycopg2.extensions import connection
from psycopg2 import connect, OperationalError
from psycopg2.errors import DuplicateDatabase, DuplicateTable

from utils import configure_logger

logger = configure_logger(log_to_file=True)


class DatabaseConnectionError(Exception):
    pass


def create_db(user: str, pwd: str, host: str, db_to_create: str) -> None:
    cnx = None
    try:
        logger.info("Establishing connection to DB postgres")
        cnx = connect(user=user, password=pwd, host=host, dbname="postgres")
        cnx.autocommit = True
        cursor = cnx.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {db_to_create}")
            logger.info("DB %s created successfully", db_to_create)
        except DuplicateDatabase as e:
            logger.error("Duplicate Database Error: %s ", str(e).rstrip())
    except OperationalError as e:
        logger.error("Connection Error: %s ", e)
    finally:
        if cnx is not None:
            logger.debug("Closing connection to DB postgres")
            cnx.close()


def connect_to_db(user: str, pwd: str, host: str, db_to_connect: str) -> connection:
    try:
        cnx = connect(user=user, password=pwd, host=host, dbname=db_to_connect)
        logger.info("Successfully connected to DB %s", db_to_connect)
        cnx.autocommit = True
        return cnx
    except psycopg2.Error as e:
        logger.error("Error %s occurred when connecting to DB %s", e, db_to_connect)
        raise DatabaseConnectionError(f"Connection to DB could not be established") from e


def create_table(cnx, qry: str):
    try:
        cursor = cnx.cursor()
        cursor.execute(qry)
        logger.info("Table created")
    except DuplicateTable as ex:
        logger.error("Duplicate Table Error: %s", str(ex).rstrip())
    except OperationalError as ex:
        logger.error("Operational Error: %s", str(ex).rstrip())


def main():
    USER = "postgres"
    HOST = "localhost"
    PWD = "coderslab"
    DB = "workshop"
    USERS_QRY = "CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(255), hashed_password VARCHAR(80))"
    MSGS_QRY = "CREATE TABLE  messages (id SERIAL PRIMARY KEY, from_id INTEGER REFERENCES users(id), to_id INTEGER REFERENCES users(id), creation_date TIMESTAMP)"

    cnx = None
    try:
        create_db(user=USER, pwd=PWD, host=HOST, db_to_create=DB)
        cnx = connect_to_db(user=USER, pwd=PWD, host=HOST, db_to_connect=DB)
        create_table(cnx, USERS_QRY)
        create_table(cnx, MSGS_QRY)
    except Exception as e:
        logger.error(e)
    finally:
        if cnx:
            logger.debug("Closing connection to %s", DB)
            cnx.close()


if __name__ == '__main__':
    main()
