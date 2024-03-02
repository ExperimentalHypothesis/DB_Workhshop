import argparse

from src.constants import USER, PWD, HOST, DB
from src.create_db import logger, connect_to_db
from src.exceptions import AuthenticationError
from src.models.user import User
from src.models.message import Message


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="enter username", type=str)
    parser.add_argument("-p", "--password", help="enter password - min 8 characters")
    parser.add_argument("-l", "--list", help="list all users", action="store_true")
    parser.add_argument("-t", "--to", help="to")
    parser.add_argument("-s", "--send", help="send message")

    return vars(parser.parse_args())


def list_user_msgs(cursor, username: str, password: str):
    user = User.load_user_by_username(cursor, username)
    if not user:
        raise ValueError(f"User {username} not exists")

    is_user_verified = user.verify_password(password)
    if not is_user_verified:
        raise AuthenticationError(f"Password {password} is incorrect")

    msgs = Message.load_all_messages(cursor, user.user_id)

    for msg in msgs:
        user = User.load_user_by_id(cursor, msg.from_id).username
        print(f"From: {user} \nMessage: {msg.text} \nDate: {msg.creation_date}\n")


def send_msg(cursor, username: str, password: str, to: str, text: str):
    sender = User.load_user_by_username(cursor, username)
    if not sender:
        raise ValueError(f"User {username} not exists")

    is_sender_verified = sender.verify_password(password)
    if not is_sender_verified:
        raise AuthenticationError(f"Password {password} is incorrect")

    receiver = User.load_user_by_username(cursor, to)
    if not receiver:
        raise ValueError(f"User {to} not exists")

    msg = Message(sender.user_id, receiver.user_id, text)
    msg.save_to_db(cursor)


def main():
    args = parse_args()
    username = args.get("username")
    password = args.get("password")
    to_list = args.get("list")
    to = args.get("to")
    send = args.get("send")

    cnx = None
    try:
        cnx = connect_to_db(user=USER, pwd=PWD, host=HOST, db_to_connect=DB)
        cursor = cnx.cursor()

        if username and password and to_list:
            list_user_msgs(cursor, username, password)
        elif username and password and to and send:
            send_msg(cursor, username, password, to, send)
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
