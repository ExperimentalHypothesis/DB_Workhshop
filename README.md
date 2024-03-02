Simple CLI app for managing user and message based on the workshop from Coderslab.

# Installation

```bash
 git clone git@github.com:ExperimentalHypothesis/DB_Workhshop.git
 cd DB_Workshop
 python -m venv venv && source venv/bin/activate
 pip install -r requirements.txt
```

# Prerequisites

You need to have a user in Postgres that can connect to default postgres DB and has grants to create tables. 
If you have it, OK just use his credentials in constants.py. If you don't have it, you need to prepare such a user first.


# Usage

Use the CLI apps as shown

#### user_app.py
```bash
python user_app.py  -l # list all users in db
python user_app.py -u <username> -p <password> # create user with given credentials
python user_app.py -u <username> -p <password> -n <new_password> -e # edits user password with given credentials
python user_app.py -u <username> -p <password> -d # deletes user with given credentials
```

#### message_app.py
```bash
python message_app.py  -u <username> -p <password> -l # list all messages for this user
python message_app.py  -u <username> -p <password> -t <username> -s "some message..." # used sends a message to another user
```