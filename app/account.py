import sqlite3
import bcrypt
from functools import wraps
from flask import g, flash

db_location = 'var/accounts.db'

def initialise_account_db(app):
    account_db = get_account_db(app)
    with app.open_resource('var/account_schema.sql', mode='r') as f:
        app.logger.info(f"Executing var/account_schema.sql")
        account_db.cursor().executescript(f.read())

def get_account_db(app):
    app.logger.info(f"Retrieving database")

    db = getattr(g, 'accounts_db', None)
    if db is None: 
        db = sqlite3.connect(db_location)
        g.accounts_db = db
    return db

def check_account_registered(app, username, email):
    app.logger.info(f"Checking if {username}, {email} is a registered account")

    db = get_account_db(app)

    result = db.cursor().execute(f"SELECT COUNT(*) FROM accounts WHERE accounts.username='{username}' OR accounts.email='{email}'")

    if(result.fetchall()[0][0] > 0):
        app.logger.info(f"{username}, {email} is already registered")
        return True
    app.logger.info(f"{username}, {email} is not registered yet.")
    return False

def register_account(app, username, email, password):
    db = get_account_db(app)

    if check_account_registered(app, username, email):
        return False
    
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    stmnt = "INSERT INTO accounts VALUES ('" + username + "', '" + email + "', '" + hashed_password.decode() + "', '" + salt.decode() + "')"
    app.logger.info(f"Excecuting statement: {stmnt}")

    try:
        db.cursor().execute(stmnt)
        db.commit()
        app.logger.info("Success")
        flash("Account registered. Please log in.")
    except:
        app.logger.info("Failed")
        flash("Failed to create your account. Please try again.")
        return False

    return True

def get_number_rows(app):
    db = get_account_db(app)

    result = db.cursor().execute("SELECT COUNT(*) FROM accounts")
    rows = result.fetchall()[0][0]

    app.logger.info(f"There are {rows} rows in the database")
    return rows

def validate_account(app, username, password):
    db = get_account_db(app)

    # Retrieve the username's related password + hash
    stmnt = f"SELECT password_hashed, salt FROM accounts WHERE accounts.username='{username}'"

    results = db.cursor().execute(stmnt).fetchall()

    if len(results) > 0:
        hashed_pass = results[0][0].encode('utf-8')
        salt = results[0][1].encode('utf-8')

        if bcrypt.hashpw(password.encode('utf-8'), salt) == hashed_pass:
            app.logger.info(f"Successfully logged in for {username}")
            return True
        else:
            flash("The username or password you entered was invalid.")
            app.logger.info(f"Failed login attempt for {username}")
            return False
    else:
        flash("The username or password you entered was invalid.")
        app.logger.info(f"Attempted to log into a non-existent account")
        return False