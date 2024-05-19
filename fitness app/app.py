import math
import string
from datetime import datetime

# Keeping cs50 SQL, to save from rewriting all SQL queries (query syntax, outputs(dictonaries to list of tuples))
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from helpers import login_required, retrieve_user, error_message
from werkzeug.security import check_password_hash, generate_password_hash

# configure application
app = Flask(__name__)
# set secret key for session
app.secret_key = "e9c85f9aa4288eb20f69a1dec03e1a9fb69a51a7df0fa46700a19ee17c14cda2"

@app.template_filter()
def datetime_format(value, current_format="%Y-%m-%d", format="%Y-%m-%d, %a"):
    """
    first, converts string date into datetime object.
    then converts datetime object into default- or given format.
    """
    return datetime.strptime(value, current_format).strftime(format)



# session configured on server-side, referenced from CS50
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# connect to database
db = SQL("sqlite:///fitnessapp.db")


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
    # clear session["workout_id"] for new workout
    session.pop("workout_id", None)

    # initialising variables
    # user id
    user_id = session.get("user_id")
    # today's date
    date = datetime.now().strftime('%Y-%m-%d')
    # current time
    start_time = datetime.now().strftime('%H:%M')

    # insert new workout into SQL workout table
    db.execute("INSERT OR IGNORE INTO workout (user_id, date, start_time) VALUES (?, ?, ?);", user_id, date, start_time)

    # set session["workout_id"] to newly-created workout
    workout_id = db.execute("SELECT id FROM workout WHERE user_id = ? AND date = ? AND start_time = ?;", user_id, date, start_time)[0].get("id")
    session["workout_id"] = workout_id

    return redirect(url_for("editworkout"))

# delete workout endpoint
@app.route("/deleteworkout", methods=["POST"])
@login_required
def deleteworkout():
    user_id = session.get("user_id")

    if request.method == "POST":
        if "delete-workout-id" in request.form:
            workout_id = request.form.get("delete-workout-id")
            db.execute("DELETE FROM workout WHERE user_id = ? AND id = ?;", user_id, workout_id)

            return redirect(url_for("index"))


# add/edit note
@app.route("/editnote", methods=["POST"])
@login_required
def editnote():
    workout_id = session.get("workout_id")

    if request.method == "POST":
        if "note" in request.form:
            note = request.form.get("note")
            db.execute("UPDATE workout SET note = ? WHERE id = ?", note, workout_id)

            return redirect(url_for("editworkout"))


# edit profile
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
                        FROM workout_set a
                        JOIN exercise b ON a.exercise_id=b.id
                        WHERE a.workout_id = ?
                        )

                        SELECT * FROM workout_data GROUP BY name, exercise_set;
                    """, 
    workout_id)

    # exercises logged in the workout
    workout_exercises = list({dict["name"] for dict in sets})

    workout_info = db.execute("SELECT * FROM workout WHERE id = ?;", workout_id)

    if request.method == "POST":
        # edit date, start- and end time
        if "editworkout-date" in request.form:
            try:
                new_date = request.form.get("editworkout-date")
                new_start_time = request.form.get("editworkout-start-time")
                new_end_time = request.form.get("editworkout-end-time")

                db.execute("UPDATE workout SET date = ?, start_time = ?, end_time = ? WHERE id = ?;", new_date, new_start_time, new_end_time, workout_id)
            except Exception as e:
                print(f"Exception editing date and time: {e}")
                return error_message("Oops, something went wrong...", 400)
            
        # delete exercise sets
        elif "delete-user-id" in request.form:
            try:
                user_id = request.form.get("delete-user-id")
                workout_id = request.form.get("delete-workout-id")
                exercise_id = request.form.get("delete-exercise-id")
                exercise_set = request.form.get("delete-exercise-set")

                db.execute("DELETE FROM workout_set WHERE user_id = ? AND workout_id = ? AND exercise_id = ? AND exercise_set = ?;", user_id, workout_id, exercise_id, exercise_set)

            except Exception as e:
                print(f"Exception deleting set: {e}")
                return error_message("Oops, something went wrong...", 400)

        # edit set
        elif "edit-user-id" in request.form:
            try:
                user_id = request.form.get("edit-user-id")
                workout_id = request.form.get("edit-workout-id")
                exercise_id = request.form.get("edit-exercise-id")
                exercise_set = request.form.get("edit-exercise-set")
                new_reps = request.form.get("edit-reps")
                new_weight = request.form.get("edit-weight")

                db.execute("""
                            UPDATE workout_set SET reps = ?, weight_kg = ?
                            WHERE user_id = ?
                            AND workout_id = ?
                            AND exercise_id = ?
                            AND exercise_set = ?
                           ;"""
                           , new_reps, new_weight, user_id, workout_id, exercise_id, exercise_set)

            except Exception as e:
                print(f"Exception editing set: {e}")
                return error_message("Oops, something went wrong...", 400)

        # add set to existing exercise
        elif "add-set" in request.form:
            try:
                user_id = request.form.get("add-user-id")
                workout_id = request.form.get("add-workout-id")
                exercise_id = request.form.get("add-exercise-id")
                add_set = request.form.get("add-set")
                add_reps = request.form.get("add-reps")
                add_weight = request.form.get("add-weight")

                # =================================================================================================== DEBUG PRINT ===================================================================================================
                print(f"try DEBUG PRINT:\nrequest form: {request.form}")

                db.execute("INSERT OR IGNORE INTO workout_set (user_id, workout_id, exercise_id, exercise_set, reps, weight_kg) VALUES(?, ?, ?, ?, ?, ?);", user_id, workout_id, exercise_id, add_set, add_reps, add_weight)

            except Exception as e:
                print(f"Exception adding set to existing exercise: {e}")
                return error_message("Oops, something went wrong...", 400)

        # log new set
        else:
            try:
                weight = request.form.get("weight")
                reps = request.form.get("reps")
                exercise_set = request.form.get("set")
                exercise_name = request.form.get("exercise")
                # exercise_name = request.form.get("exercise").lower()
                exercise_id = db.execute("SELECT id FROM exercise WHERE name = ?;", exercise_name)[0].get("id")

                # insert row into workout_set table
                db.execute("INSERT OR IGNORE INTO workout_set (user_id, workout_id, exercise_id, exercise_set, reps, weight_kg) VALUES (?, ?, ?, ?, ?, ?);", user_id, workout_id, exercise_id, exercise_set, reps, weight)

                # =================================================================================================== DEBUG PRINT ===================================================================================================
                print(f"try DEBUG PRINT:\nrequest form: {request.form}")

            except Exception as e:
                print(f"Exception logging new set: {e}")
                print(f"except DEBUG PRINT:\nrequest form: {request.form}")
                return error_message("Invalid exercise name.", 400)

        return redirect(url_for("editworkout"))

    return render_template("editworkout.html", sets=sets, workout_exercises=workout_exercises, workout_info=workout_info)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session.get("user_id")
    workout_history = db.execute("SELECT * FROM workout WHERE user_id = ? ORDER BY date DESC, start_time DESC LIMIT 5;", user_id)

    avg_workout_duration_min = db.execute("""
                                            WITH durations AS (
                                            SELECT date, time(end_time, "-"||strftime('%H', start_time)||" hours", "-"||strftime('%M', start_time)||" minutes") workout_duration
                                            FROM workout
                                            WHERE user_id = ?
                                            AND end_time IS NOT NULL
                                            AND start_time IS NOT NULL)

                                            SELECT AVG((strftime('%H', workout_duration)*60)+strftime('%M', workout_duration)) avg_workout_duration_min FROM durations;
                                            """, user_id)[0]["avg_workout_duration_min"]

    # handle error caused, when query returns no results
    try:
        days_since_last_workout = db.execute("""
                                                SELECT (JULIANDAY(date('now'))-JULIANDAY(date)) AS days_since_last_workout
                                                FROM workout WHERE user_id = ? ORDER BY date DESC LIMIT 1;
                                                """, user_id)[0]["days_since_last_workout"]
    except:
        days_since_last_workout = 0

    workouts_last_7_days = db.execute("""
                                            SELECT COUNT(*) AS workouts_last_7_days
                                            FROM workout WHERE user_id = ? AND date > DATE(JULIANDAY('now')-7);
                                        """, user_id)[0]["workouts_last_7_days"]

    workouts_last_30_days = db.execute("""
                                            SELECT COUNT(*) AS workouts_last_30_days
                                            FROM workout WHERE user_id = ? AND date > DATE(JULIANDAY('now')-30);
                                        """, user_id)[0]["workouts_last_30_days"]

    workouts_last_90_days = db.execute("""
                                            SELECT COUNT(*) AS workouts_last_90_days
                                            FROM workout WHERE user_id = ? AND date > DATE(JULIANDAY('now')-90);
                                        """, user_id)[0]["workouts_last_90_days"]

    total_volume_lifted = db.execute("""
                                        SELECT SUM(reps*weight_kg) AS total_volume_lifted
                                        FROM workout a
                                        JOIN workout_set b ON a.id=b.workout_id
                                        JOIN exercise c ON b.exercise_id=c.id
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

    # load specific edit workout page
    if request.method == "POST":
        if "edit-workout-id" in request.form:
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

        # user details, retrieved from database
        request_username = request.form.get("username")
        user = retrieve_user(db, request_username)

        # check user info exists
        if user == None:
            return error_message("Invalid user name or password.", 403)

        # compare user password with received password via check_password_hash(hashed_password, plain_text_password).
        # if password incorrect, return error message
        if not check_password_hash(user.get("password_hash"), request.form.get("password")):
            return error_message("Invalid user name or password.", 403)

        # if username and password pass, save user id and username to session
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
    profile = db.execute("SELECT * FROM user WHERE id=?;", user_id)[0]

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


@app.route("/register_login", methods=["GET", "POST"])
def register_login():

    # post form - login details and email
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")
        email = request.form.get("email")
 
        # check, if password matches password_confirmation
        if password != password_confirmation:
            flash("Password needs to match Confirm Password.")
            return render_template("register_login.html")

        """
            check password strength
            password must contain at least one of each:
                - lowercase letter
                - uppercase letter
                - number
                - symbol

            using generators for efficiency
        """
        if (not any(character in password for character in list(string.digits)) or
            not any(character in password for character in list(string.ascii_lowercase)) or
            not any(character in password for character in list(string.ascii_uppercase)) or
            not any(character in password for character in list(string.punctuation))):
            flash("Password needs to contain at least one lowercase letter, uppercase letter, number and symbol.")
            return render_template("register_login.html")

        # check, if username is taken
        if retrieve_user(db, "username") != None:
            flash("Username already taken. Please choose another one.")
            return render_template("register_login.html")

        # create new user in database
        try:
            db.execute("""INSERT INTO user (username, password_hash, email) VALUES (?, ?, ?);""",
                        username, generate_password_hash(password), email)
        except Exception as e:
            print(f"Registration error:\n{e}")
            flash("Error encountered, please try again.\nIf error persists, kindly contact support.")
            return render_template("register_login.html")
        
        # login newly-created user
        session.clear()
        user = retrieve_user(db, username)

        # check user info exists
        if user == None:
            return error_message("Invalid user name or password.", 403)

        # save user id and user name to session
        session["user_id"] = user.get("id")
        session["user_name"] = user.get("username")

        # redirect to register details page.
        return redirect(url_for("register_details"))

    return render_template("register_login.html")

@app.route("/register_details", methods=["GET", "POST"])
def register_details():

    print(f"PRINT USER ID: {session.get('user_id')}")

    # post form - profile details
    if request.method == "POST":
        user_id = session.get("user_id")
        first_name = request.form.get("firstname")
        last_name = request.form.get("lastname")
        date_of_birth = request.form.get("date-of-birth")
        height = request.form.get("height")
        weight = request.form.get("weight")

        # update user record
        db.execute("""
                        UPDATE user
                        SET first_name = ?,
                            last_name = ?,
                            date_of_birth = ?,
                            height_cm = ?,
                            weight_kg = ?
                        WHERE id = ?
                        ;
                    """,
                    first_name, last_name, date_of_birth, height, weight, user_id)

        # redirect to homepage
        return redirect(url_for("index"))

    return render_template("register_details.html")


@app.route("/workouthistory", methods=["GET", "POST"])
@login_required
def workouthistory():
    user_id = session.get("user_id")

    # pagination - workout history, showing 10 workouts per page
    workouts_sum = db.execute("SELECT COUNT() sum FROM workout WHERE user_id = ?;", user_id)[0].get("sum")
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
                                    FROM workout
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
                                    FROM workout
                                    WHERE user_id = ?
                                    )
                                    SELECT * FROM t WHERE row_num > ? AND row_num <= ?;

                                    """, user_id, row_num_start, row_num_end)


    if request.method == "POST":
        if "delete-workout-id" in request.form:
            workout_id = request.form.get("delete-workout-id")
            db.execute("DELETE FROM workout WHERE user_id=? AND id=?", user_id, workout_id)

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



