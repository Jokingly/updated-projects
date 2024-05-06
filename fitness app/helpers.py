from flask import redirect, render_template, request, session, url_for
from functools import wraps


def error_message(message, code=400):
    """Render error message to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("error_message.html", top=code, bottom=escape(message)), code


# login_required wrapper from CS50
def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# return user dict from (SQLite3) fitnessapp.db table users. returns None, if there's an error.
# takes database variable and string as arguments, respectively.
def retrieve_user(database, username_form_id):
        try:
            # returns first dictionary matching username provided via username_form_id
            return database.execute("SELECT * FROM users WHERE username = ?;", request.form.get(username_form_id))[0]

        except:
            # return None, if error encountered
            return None




