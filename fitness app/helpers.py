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
    return render_template("error_message.html", code=code, message=escape(message))


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
def retrieve_user(database, username):
        try:
            # retrieve user info from db
            return database.execute("SELECT * FROM user WHERE username = ?;", username)[0]

        except:
            return None

# convert lbs to kg
def lbs_kg_conversion(number, decimal_places=0):
    lbs_kg_divider = 0.4535924
    return round(number * lbs_kg_divider, decimal_places)

