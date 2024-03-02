from datetime import datetime

from src.constants import USER, PWD, HOST, DB
from src.create_db import logger, connect_to_db
from src.models.user import User


class Message:
    def __init__(self, from_id: int, to_id: int, text: str, creation_date: datetime = None, id_: int | None = None):
        self.from_id = from_id
        self.to_id = to_id
        self.text = text
        self.creation_date = creation_date
        self._id = id_ or -1

    @property
    def message_id(self):
        return self._id

    def save_to_db(self, cursor):
        try:
            cursor.execute("""
            INSERT INTO messages (from_id, to_id, text, creation_date) VALUES (%s, %s, %s, %s)
            RETURNING id
            """, (self.from_id, self.to_id, self.text, datetime.now()))
            self._id = cursor.fetchone()[0]
            logger.debug("Message with id %s inserted successfully", self.message_id)
        except Exception as e:
            cursor.connection.rollback()
            logger.error("Failed to insert message: ", e)

    @classmethod
    def load_all_messages(cls, cursor, user_id: int):
        cursor.execute("SELECT from_id, to_id, text, creation_date, id FROM messages WHERE to_id = %s", (user_id,))
        msg_data = cursor.fetchall()
        return [cls(*msg) for msg in msg_data]


# to test it briefly
if __name__ == "__main__":

    cnx = None
    try:
        cnx = connect_to_db(user=USER, pwd=PWD, host=HOST, db_to_connect=DB)
        cursor = cnx.cursor()
        users = User.load_all_users(cursor)
        assert users != 0

        msgs = [Message(from_id=users[0].user_id, to_id=users[1].user_id, text="ahoj"),
                Message(from_id=users[1].user_id, to_id=users[0].user_id, text="cau")]

        # save all
        for msg in msgs:
            assert msg.message_id == -1
            msg.save_to_db(cursor)
            assert msg.message_id != -1

        # load all from both users
        msgs = Message.load_all_messages(cursor, users[0].user_id)
        for msg in msgs:
            assert msg.text == "cau"
        msgs = Message.load_all_messages(cursor, users[1].user_id)
        for msg in msgs:
            assert msg.text == "ahoj"

    except Exception as e:
        logger.error(e)
    finally:
        if cnx:
            logger.debug("Closing connection to DB %s", DB)
            cnx.close()