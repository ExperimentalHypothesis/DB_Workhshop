
# normally these values would be stored as secrets and read as environment vars
USER = "lukas"
HOST = "localhost"
PWD = "lukaspwd"
DB = "exam"

USERS_QRY = "CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(255) UNIQUE, hashed_password VARCHAR(80))"
MSGS_QRY = "CREATE TABLE  messages (id SERIAL PRIMARY KEY, from_id INTEGER REFERENCES users(id), to_id INTEGER REFERENCES users(id), text TEXT, creation_date TIMESTAMP)"
