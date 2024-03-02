import logging
import psycopg2
from psycopg2.extensions import connection
from psycopg2 import connect, OperationalError
from psycopg2.errors import DuplicateDatabase, DuplicateTable

from src.constants import USER, PWD, HOST, DB, USERS_QRY, MSGS_QRY
from src.exceptions import DatabaseConnectionError
from src.utils import configure_logger

logger = configure_logger(level=logging.DEBUG, log_to_file=False)


def create_db(user: str, pwd: str, host: str, db_to_create: str) -> None:
    cnx = None
    try:
        logger.debug("Establishing connection to DB postgres")
        cnx = connect(user=user, password=pwd, host=host, dbname="postgres")
        cnx.autocommit = True
        cursor = cnx.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {db_to_create}")
            logger.debug("DB %s created successfully", db_to_create)
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
        cnx.autocommit = True
        logger.debug("Successfully connected to DB %s", db_to_connect)
        return cnx
    except psycopg2.Error as e:
        logger.error("Error %s occurred when connecting to DB %s", e, db_to_connect)
        raise DatabaseConnectionError(f"Connection to DB {db_to_connect} failed") from e


def create_table(cnx: connection, qry: str) -> None:
    try:
        cursor = cnx.cursor()
        cursor.execute(qry)
        logger.debug("Table created")
    except DuplicateTable as ex:
        logger.error("Duplicate Table Error: %s", str(ex).rstrip())
    except OperationalError as ex:
        logger.error("Operational Error: %s", str(ex).rstrip())


def main():
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



