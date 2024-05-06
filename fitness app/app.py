# might not need datetime module
# import datetime
import math
import string
import sqlite3

# from cs50 import SQL # Deprecated
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from helpers import login_required, retrieve_user, error_message
from werkzeug.security import check_password_hash, generate_password_hash

# configure application
app = Flask(__name__)
# set secret key for session
app.secret_key = "e9c85f9aa4288eb20f69a1dec03e1a9fb69a51a7df0fa46700a19ee17c14cda2"

# session configured on server-side, referenced from CS50
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# connect to SQLite3 database via CS50 library
# db = SQL("sqlite:///fitnessapp.db") # # Deprecated

# SQLite3 connection
try:
    con = sqlite3.connect("fitnessapp.db")
    db = con.cursor()
    print("SQLite3 DB connection successful.")
except Exception as e:
    print(f"Error: '{e}'")


# referenced from CS50 to not cache responses
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    user_id = session.get("user_id")

    if request.method == "POST":
        user_hash = db.execute("SELECT hash FROM users WHERE id = ?;", user_id)[0].get("hash")
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")
        confirm_password = request.form.get("confirm-password")

        # if old_password doesn't match hash, return error
        if not check_password_hash(user_hash, old_password):
            flash("Old Password invalid.")
            return render_template("changepassword.html")

        # if password and password_confirmation mismatch, return error
        if new_password != confirm_password:
            flash("New Password needs to match Confirm Password.")
            return render_template("changepassword.html")

        # check if password contains at least one lowercase letter, uppercase letter, number and symbol
        # using generators for memory efficiency
        if (not any(character in new_password for character in list(string.digits)) or
            not any(character in new_password for character in list(string.ascii_lowercase)) or
            not any(character in new_password for character in list(string.ascii_uppercase)) or
            not any(character in new_password for character in list(string.punctuation))):
            flash("Password needs to contain at least one lowercase letter, uppercase letter, number and symbol.")
            return render_template("changepassword.html")

        # upon passing above tests, create new user
        # this is done by inserting the username and password in the users table
        db.execute("UPDATE users SET hash = ? WHERE id = ?;", generate_password_hash(new_password), user_id)

        # if password update successful, flash message and redirect to profile page
        flash("Password update successful!")
        return redirect(url_for("profile"))

    return render_template("changepassword.html")


@app.route("/createworkout", methods=["GET", "POST"])
@login_required
def createworkout():
    # if workout id already exists in session, append exercises to it
    if request.method == "POST":
        # clear session["workout_id"] to create new workout record
        session.pop("workout_id", None)

        # initialising variables
        user_id = session.get("user_id")
        date = request.form.get("date")
        start_time = request.form.get("start-time")

        # create row in "workouts" table
        db.execute("INSERT OR IGNORE INTO workouts (user_id, date, start_time) VALUES (?, ?, ?);", user_id, date, start_time)

        # initialise workout_id with id of newly created workout and save it in session under "workout_id"
        workout_id = db.execute("SELECT id FROM workouts WHERE user_id = ? AND date = ? AND start_time = ?;", user_id, date, start_time)[0].get("id")
        session["workout_id"] = workout_id

        return redirect(url_for("editworkout"))

    return render_template("createworkout.html")


@app.route("/editprofile", methods=["GET", "POST"])
@login_required
def editprofile():
    user_id = session.get("user_id")

    # query user data
    profile = db.execute("SELECT * FROM users WHERE id = ?;", user_id)[0]

    # add user data to dictionary to be passed to "editprofile.html"
    profile_data = dict()
    profile_data["username"] = profile.get("username")
    profile_data["first_name"] = profile.get("first_name")
    profile_data["last_name"] = profile.get("last_name")
    profile_data["date_of_birth"] = profile.get("date_of_birth")
    profile_data["height"] = profile.get("height_cm")
    profile_data["weight"] = profile.get("weight_kg")

    # NEEDS TESTING
    if request.method == "POST":

        # get form data
        new_first_name = request.form.get("edit-first-name")
        new_last_name = request.form.get("edit-last-name")
        new_date_of_birth = request.form.get("edit-date-of-birth")
        new_height = request.form.get("edit-height")
        new_weight = request.form.get("edit-weight")

        # if input value passed is new and not empty update relevant column
        if new_first_name != profile_data["first_name"] and new_first_name != "":
            db.execute("UPDATE OR IGNORE users SET first_name = ? WHERE id = ?;", new_first_name, user_id)

        if new_last_name != profile_data["last_name"] and new_last_name != "":
            db.execute("UPDATE OR IGNORE users SET last_name = ? WHERE id = ?;", new_last_name, user_id)

        if new_date_of_birth != profile_data["date_of_birth"] and new_date_of_birth != "":
            db.execute("UPDATE OR IGNORE users SET date_of_birth = ? WHERE id = ?;", new_date_of_birth, user_id)

        if new_height != profile_data["height"] and new_height != "":
            db.execute("UPDATE OR IGNORE users SET height_cm = ? WHERE id = ?;", new_height, user_id)

        if new_weight != profile_data["weight"] and new_weight != "":
            db.execute("UPDATE OR IGNORE users SET weight_kg = ? WHERE id = ?;", new_weight, user_id)

        return redirect(url_for("profile"))

    return render_template("editprofile.html", profile_data=profile_data)


@app.route("/editworkout", methods=["GET", "POST"])
@login_required
def editworkout():
    user_id = session.get("user_id")
    workout_id = session.get("workout_id")

    # select workout data via SQL
    sets = db.execute("""
                            WITH workout_data AS (
                            SELECT *
                            FROM sets a
                            JOIN exercises b ON a.exercise_id=b.id
                            WHERE a.workout_id = ?
                            )

                            SELECT * FROM workout_data GROUP BY exercise, exercise_set;
    """, workout_id)

    workout_info = db.execute("SELECT * FROM workouts WHERE id = ?;", workout_id)

    if request.method == "POST":
        # edit date, start- and end time
        if "editworkout-date" in request.form:
            new_date = request.form.get("editworkout-date")
            new_start_time = request.form.get("editworkout-start-time")
            new_end_time = request.form.get("editworkout-end-time")

            db.execute("UPDATE workouts SET date = ?, start_time = ?, end_time = ? WHERE id = ?;", new_date, new_start_time, new_end_time, workout_id)

        # delete exercise sets
        elif "delete-user-id" in request.form:
            try:
                user_id = request.form.get("delete-user-id")
                workout_id = request.form.get("delete-workout-id")
                exercise_id = request.form.get("delete-exercise-id")
                exercise_set = request.form.get("delete-exercise-set")

                db.execute("DELETE FROM sets WHERE user_id = ? AND workout_id = ? AND exercise_id = ? AND exercise_set = ?;", user_id, workout_id, exercise_id, exercise_set)

            except:
                return error_message("Oops, something went wrong...", 400)

        # log new set in workout
        else:
            try:
                weight = request.form.get("weight")
                reps = request.form.get("reps")
                exercise_set = request.form.get("set")
                exercise_name = request.form.get("exercise").lower()
                exercise_id = db.execute("SELECT id FROM exercises WHERE exercise = ?;", exercise_name)[0].get("id")

                # insert row into sets table
                db.execute("INSERT OR IGNORE INTO sets (user_id, workout_id, exercise_id, exercise_set, reps, weight_kg) VALUES (?, ?, ?, ?, ?, ?);", user_id, workout_id, exercise_id, exercise_set, reps, weight)

            except:
                return error_message("Invalid exercise name.", 400)

        return redirect(url_for("editworkout"))

    return render_template("editworkout.html", sets=sets, workout_info=workout_info)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session.get("user_id")
    workout_history = db.execute("SELECT * FROM workouts WHERE user_id = ? ORDER BY date DESC, start_time DESC LIMIT 5;", user_id)

    avg_workout_duration_min = db.execute("""
                                            WITH durations AS (
                                            SELECT date, time(end_time, "-"||strftime('%H', start_time)||" hours", "-"||strftime('%M', start_time)||" minutes") workout_duration
                                            FROM workouts
                                            WHERE user_id = ?
                                            AND end_time IS NOT NULL
                                            AND start_time IS NOT NULL)

                                            SELECT AVG((strftime('%H', workout_duration)*60)+strftime('%M', workout_duration)) avg_workout_duration_min FROM durations;
                                            """, user_id)[0]["avg_workout_duration_min"]

    # handle error caused, when query returns no results
    try:
        days_since_last_workout = db.execute("""
                                                SELECT (JULIANDAY(date('now'))-JULIANDAY(date)) AS days_since_last_workout
                                                FROM workouts WHERE user_id = ? ORDER BY date DESC LIMIT 1;
                                                """, user_id)[0]["days_since_last_workout"]
    except:
        days_since_last_workout = 0

    workouts_last_7_days = db.execute("""
                                            SELECT COUNT(*) AS workouts_last_7_days
                                            FROM workouts WHERE user_id = ? AND date > DATE(JULIANDAY('now')-7);
                                        """, user_id)[0]["workouts_last_7_days"]

    workouts_last_30_days = db.execute("""
                                            SELECT COUNT(*) AS workouts_last_30_days
                                            FROM workouts WHERE user_id = ? AND date > DATE(JULIANDAY('now')-30);
                                        """, user_id)[0]["workouts_last_30_days"]

    workouts_last_90_days = db.execute("""
                                            SELECT COUNT(*) AS workouts_last_90_days
                                            FROM workouts WHERE user_id = ? AND date > DATE(JULIANDAY('now')-90);
                                        """, user_id)[0]["workouts_last_90_days"]

    total_volume_lifted = db.execute("""
                                        SELECT SUM(reps*weight_kg) AS total_volume_lifted
                                        FROM workouts a
                                        JOIN sets b ON a.id=b.workout_id
                                        JOIN exercises c ON b.exercise_id=c.id
                                        WHERE a.user_id = ?;
                                    """, user_id)[0]["total_volume_lifted"]

    dashboard = dict()
    dashboard["avg_workout_duration_min"] = avg_workout_duration_min
    dashboard["days_since_last_workout"] = days_since_last_workout
    dashboard["workouts_last_7_days"] = workouts_last_7_days
    dashboard["workouts_last_30_days"] = workouts_last_30_days
    dashboard["workouts_last_90_days"] = workouts_last_90_days

    # handle error when query from total_volume_lifted (above) returns None data type
    try:
        dashboard["total_volume_lifted"] = "{:,}".format(total_volume_lifted)
    except:
        dashboard["total_volume_lifted"] = 0


    if request.method == "POST":
        if "delete-workout-id" in request.form:
            workout_id = request.form.get("delete-workout-id")
            db.execute("DELETE FROM workouts WHERE user_id = ? AND id = ?;", user_id, workout_id)

            return redirect(url_for("index"))

        elif "edit-workout-id" in request.form:
            workout_id = request.form.get("edit-workout-id")
            session["workout_id"] = workout_id

            return redirect(url_for("editworkout"))

    # pass dictionary into render_template, with dictionary with dashboard data as key value pairs?
    return render_template("index.html", workout_history=workout_history, dashboard=dashboard)


@app.route("/login", methods=["GET", "POST"])
def login():
    # clear session, if login request received
    if request.method == "POST":
        session.clear()

        # store user dictionary from the database in an object
        user = retrieve_user(db, "username")

        # check username exists, else return error message
        if user == None:
            return error_message("Invalid user name or password.", 403)

        # compare user password with received password via check_password_hash(hashed_password, plain_text_password).
        # if password incorrect, return error message
        if not check_password_hash(user.get("hash"), request.form.get("password")):
            return error_message("Invalid user name or password.", 403)

        # if username and password pass, save user id to session
        session["user_id"] = user.get("id")
        session["user_name"] = user.get("username")

        # redirect to homepage after successful login
        return redirect(url_for("index"))

    # render login page
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.pop("user_id", None)

    return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session.get("user_id")
    profile = db.execute("SELECT * FROM users WHERE id=?;", user_id)[0]

    profile_data = dict()
    profile_data["id"] = profile.get("id")
    profile_data["username"] = profile.get("username")
    profile_data["first_name"] = profile.get("first_name")
    profile_data["last_name"] = profile.get("last_name")
    profile_data["date_of_birth"] = profile.get("date_of_birth")
    profile_data["member_since"] = profile.get("member_since")
    profile_data["height_cm"] = profile.get("height_cm")
    profile_data["weight_kg"] = profile.get("weight_kg")

    return render_template("profile.html", profile_data=profile_data)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        first_name = request.form.get("firstname")
        last_name = request.form.get("lastname")
        date_of_birth = request.form.get("date-of-birth")
        height = request.form.get("height")
        weight = request.form.get("weight")

        # if password and password_confirmation mismatch, return error
        if password != password_confirmation:
            flash("Password needs to match Confirm Password.")
            return render_template("register.html")

        # check if password contains at least one lowercase letter, uppercase letter, number and symbol
        # using generators for efficiency
        if (not any(character in password for character in list(string.digits)) or
            not any(character in password for character in list(string.ascii_lowercase)) or
            not any(character in password for character in list(string.ascii_uppercase)) or
            not any(character in password for character in list(string.punctuation))):
            flash("Password needs to contain at least one lowercase letter, uppercase letter, number and symbol.")
            return render_template("register.html")

        # if username already taken (exists in database), return error
        if retrieve_user(db, "username") != None:
            flash("Username already taken. Please choose another one.")
            return render_template("register.html")

        # ====================================== TROUBLE SHOOTING ======================================
        # upon passing above tests, create new user
        # this is done by inserting the username and password in the users table
        db.execute("""INSERT INTO users
                    (username, hash, first_name, last_name, date_of_birth, height_cm, weight_kg)
                    VALUES (?, ?, ?, ?, ?, ?, ?);""",
                    (username, generate_password_hash(password), first_name, last_name, date_of_birth, height, weight))

        # Upon successful registration redirect to homepage.
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/workouthistory", methods=["GET", "POST"])
@login_required
def workouthistory():
    user_id = session.get("user_id")

    # pagination - workout history, showing 10 workouts per page
    workouts_sum = db.execute("SELECT COUNT() sum FROM workouts WHERE user_id = ?;", user_id)[0].get("sum")
    workouts_per_page = 10
    number_of_pages = math.ceil(workouts_sum / workouts_per_page)
    pages = list(range(1, number_of_pages + 1))

    # if "workout_history_page" cookie is undefined, then set it to page 1
    if session.get("workout_history_page") == None:
        session["workout_history_page"] = 1

    current_page = session.get("workout_history_page")
    row_num_start = (current_page - 1) * workouts_per_page
    row_num_end = current_page * workouts_per_page

    # if session["workout_history_date_order_switch"] is None, set it to "DESC" order by default:
    if session.get("workout_history_date_order_switch") == None:
        session["workout_history_date_order_switch"] = "DESC"

    if session["workout_history_date_order_switch"] == "DESC":
        workout_history = db.execute("""
                                    WITH t AS (
                                    SELECT ROW_NUMBER () OVER (ORDER BY date DESC) row_num,
                                    id,
                                    date,
                                    start_time,
                                    end_time
                                    FROM workouts
                                    WHERE user_id = ?
                                    )
                                    SELECT * FROM t WHERE row_num > ? AND row_num <= ?;

                                    """, user_id, row_num_start, row_num_end)

    elif session["workout_history_date_order_switch"] == "ASC":
        workout_history = db.execute("""
                                    WITH t AS (
                                    SELECT ROW_NUMBER () OVER (ORDER BY date ASC) row_num,
                                    id,
                                    date,
                                    start_time,
                                    end_time
                                    FROM workouts
                                    WHERE user_id = ?
                                    )
                                    SELECT * FROM t WHERE row_num > ? AND row_num <= ?;

                                    """, user_id, row_num_start, row_num_end)


    if request.method == "POST":
        if "delete-workout-id" in request.form:
            workout_id = request.form.get("delete-workout-id")
            db.execute("DELETE FROM workouts WHERE user_id=? AND id=?", user_id, workout_id)

            return redirect(url_for("workouthistory"))

        if "edit-workout-id" in request.form:
            workout_id = request.form.get("edit-workout-id")
            session["workout_id"] = workout_id

            return redirect(url_for("editworkout"))

        if "prev-page" in request.form:
            prev_page = session.get("workout_history_page") + int(request.form.get("prev-page"))
            if prev_page >= 1:
                session["workout_history_page"] = prev_page

                return redirect(url_for("workouthistory"))

        if "next-page" in request.form:
            next_page = session.get("workout_history_page") + int(request.form.get("next-page"))
            if next_page <= number_of_pages:
                session["workout_history_page"] = next_page

                return redirect(url_for("workouthistory"))

        if "change-page" in request.form:
            page = int(request.form.get("change-page"))
            if page in pages:
                session["workout_history_page"] = page

                return redirect(url_for("workouthistory"))

        if "date-sort" in request.form:
            if session["workout_history_date_order_switch"] == "DESC":
                session["workout_history_date_order_switch"] = "ASC"

            elif session["workout_history_date_order_switch"] == "ASC":
                session["workout_history_date_order_switch"] = "DESC"

            return redirect(url_for("workouthistory"))


    return render_template("workouthistory.html", workout_history=workout_history, pages=pages)



