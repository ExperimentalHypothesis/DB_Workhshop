import argparse

from src.constants import USER, PWD, HOST, DB
from src.create_db import logger, connect_to_db
from src.exceptions import UniqueViolationError, AuthenticationError
from src.models.user import User
from src.utils import validate_password_len


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="enter username", type=str)
    parser.add_argument("-p", "--password", help="enter password - min 8 characters")
    parser.add_argument("-n", "--new_pass", help="enter new password - min 8 characters")
    parser.add_argument("-l", "--list", help="list all users", action="store_true")
    parser.add_argument("-d", "--delete", help="delete a user", action="store_true")
    parser.add_argument("-e", "--edit", help="edit a user", action="store_true")

    return vars(parser.parse_args())


def create_user(cursor, username: str, pwd: str):
    validate_password_len(pwd)
    user = User.load_user_by_username(cursor, username)
    if user:
        raise UniqueViolationError(f"User with username {username} already exists")
    new_user = User(username, pwd)
    new_user.save_to_db(cursor)


def edit_user(cursor, username: str, new_pwd: str):
    validate_password_len(new_pwd)
    user = User(username, new_pwd)
    user.save_to_db(cursor)


def delete_user(cursor, username: str, password: str):
    user = User.load_user_by_username(cursor, username)
    if not user:
        raise ValueError(f"User {username} does not exist")

    is_user_verified = user.verify_password(password)
    if not is_user_verified:
        raise AuthenticationError(f"Password {password} is incorrect")

    if user and is_user_verified:
        user.delete(cursor)


def list_users(cursor):
    for u in User.load_all_users(cursor):
        print(u)


def main():
    args = parse_args()
    username = args.get("username")
    password = args.get("password")
    new_pass = args.get("new_pass")
    to_list = args.get("list")
    to_delete = args.get("delete")
    to_edit = args.get("edit")

    cnx = None
    try:
        cnx = connect_to_db(user=USER, pwd=PWD, host=HOST, db_to_connect=DB)
        cursor = cnx.cursor()

        if username and password and new_pass and to_edit:
            edit_user(cursor, username, new_pass)
        elif username and password and to_delete:
            delete_user(cursor, username, password)
        elif username and password:
            create_user(cursor, username, password)
        elif to_list:
            list_users(cursor)
        else:
            logger.error("Invalid combination of inputs")

    except Exception as e:
        logger.error(e)
    finally:
        if cnx:
            logger.debug("Closing connection to DB %s", DB)
            cnx.close()


if __name__ == "__main__":
    main()