import bcrypt

from src.constants import USER, PWD, HOST, DB
from src.create_db import logger, connect_to_db


class User:
    def __init__(self, username: str, password: str = "", id_: int | None = None):
        self.username = username
        self.password = password
        self._id = id_ or -1

    def __repr__(self):
        return f"<User: {self.user_id} {self.username}>"

    @property
    def user_id(self):
        return self._id

    @property
    def password(self):
        return self._hashed_password

    @password.setter
    def password(self, new_password: str):
        self._hashed_password = self.hash_password(new_password)

    def save_to_db(self, cursor) -> None:
        try:
            cursor.execute("""
            INSERT INTO users (username, hashed_password) VALUES (%s, %s)
            ON CONFLICT (username) DO UPDATE SET hashed_password = EXCLUDED.hashed_password
            RETURNING id
            """, (self.username, self._hashed_password))
            self._id = cursor.fetchone()[0]
            logger.debug("User %s upserted successfully", self)
        except Exception as e:
            cursor.connection.rollback()
            logger.error("Failed to upsert user:", e)

    def delete(self, cursor):
        try:
            cursor.execute("DELETE FROM users WHERE id=%s", (self.user_id,))
            logger.debug("User %s deleted successfully", self)
            self._id = -1
        except Exception as e:
            cursor.connection.rollback()
            logger.error("Failed to delete user:", e)

    @classmethod
    def load_user_by_username(cls, cursor, username: str):
        cursor.execute("SELECT username, hashed_password, id FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            return cls.create_user(user_data)

    @classmethod
    def load_user_by_id(cls, cursor, id_: int):
        cursor.execute("SELECT username, hashed_password, id FROM users WHERE id = %s", (id_,))
        user_data = cursor.fetchone()
        if user_data:
            return cls.create_user(user_data)

    @classmethod
    def load_all_users(cls, cursor):
        cursor.execute("SELECT username, hashed_password, id FROM users")
        users_data = cursor.fetchall()
        return [cls.create_user(u) for u in users_data]

    @classmethod
    def create_user(cls, user_data):
        username, hashed_password, id_ = user_data
        user = cls(username=username, id_=id_)
        user._hashed_password = hashed_password
        return user

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode()

    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


# to test it briefly
if __name__ == "__main__":
    users = [User(username="lukas", password="lukaspwd"),
             User(username="martin", password="martinpwd"),
             User(username="pavel", password="pavelpwd")]

    cnx = None
    try:
        cnx = connect_to_db(user=USER, pwd=PWD, host=HOST, db_to_connect=DB)
        cursor = cnx.cursor()

        # save all
        for user in users:
            assert user.user_id == -1
            user.save_to_db(cursor)
            assert user.user_id != -1

        # get marting by name and change his password
        martin = User.load_user_by_username(cursor, "martin")
        martin.password = "somenewpwd"
        martin.save_to_db(cursor)

        # get all - there should be 3
        users = User.load_all_users(cursor)
        assert len(users) == 3

        # delete martin
        User.load_user_by_username(cursor, "martin").delete(cursor)

        # get all - martin should be gone
        users = User.load_all_users(cursor)
        assert len(users) == 2

    except Exception as e:
        logger.error(e)
    finally:
        if cnx:
            logger.debug("Closing connection to DB %s", DB)
            cnx.close()