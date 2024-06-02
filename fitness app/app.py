import math
import pandas as pd
import plotly.express as px
import string
from datetime import datetime

# Keeping cs50 SQL, to save from rewriting all SQL queries (query syntax, outputs(dictonaries to list of tuples))
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from helpers import login_required, retrieve_user, error_message, lbs_kg_conversion
from werkzeug.security import check_password_hash, generate_password_hash

# configure application
app = Flask(__name__)

# set secret key for session
app.secret_key = "e9c85f9aa4288eb20f69a1dec03e1a9fb69a51a7df0fa46700a19ee17c14cda2"


# Jinja2 function to format datetime
# used in editworkout.html among other places
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
    user_id = session.get("user_id", None)

    if request.method == "POST":
        user_hash = db.execute("SELECT hash FROM user WHERE id = ?;", user_id)[0].get("hash", None)
        old_password = request.form.get("old-password", None)
        new_password = request.form.get("new-password", None)
        confirm_password = request.form.get("confirm-password", None)

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
        # this is done by inserting the username and password in the user table
        db.execute("UPDATE user SET hash = ? WHERE id = ?;", generate_password_hash(new_password), user_id)

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
    user_id = session.get("user_id", None)
    # today's date
    date = datetime.now().strftime('%Y-%m-%d')
    # current time
    start_time = datetime.now().strftime('%H:%M')

    # insert new workout into SQL workout table
    db.execute("INSERT OR IGNORE INTO workout (user_id, date, start_time) VALUES (?, ?, ?);", user_id, date, start_time)

    # set session["workout_id"] to newly-created workout
    workout_id = db.execute("SELECT id FROM workout WHERE user_id = ? AND date = ? AND start_time = ?;", user_id, date, start_time)[0].get("id", None)
    session["workout_id"] = workout_id

    return redirect(url_for("editworkout"))

# delete workout endpoint
@app.route("/deleteworkout", methods=["POST"])
@login_required
def deleteworkout():
    user_id = session.get("user_id", None)

    if request.method == "POST":
        if "delete-workout-id" in request.form:
            workout_id = request.form.get("delete-workout-id", None)
            db.execute("DELETE FROM workout WHERE user_id = ? AND id = ?;", user_id, workout_id)

            return redirect(url_for("index"))


# add/edit note
@app.route("/editnote", methods=["POST"])
@login_required
def editnote():
    workout_id = session.get("workout_id", None)

    if request.method == "POST":
        if "note" in request.form:
            note = request.form.get("note", None)
            db.execute("UPDATE workout SET note = ? WHERE id = ?", note, workout_id)

            return redirect(url_for("editworkout"))


# edit profile
@app.route("/editprofile", methods=["GET", "POST"])
@login_required
def editprofile():
    user_id = session.get("user_id", None)

    # query user data
    profile = db.execute("SELECT * FROM user WHERE id = ?;", user_id)[0]

    if request.method == "POST":

        # get form data
        new_first_name = request.form.get("edit-first-name", None)
        new_last_name = request.form.get("edit-last-name", None)
        new_date_of_birth = request.form.get("edit-date-of-birth", None)
        new_height = request.form.get("edit-height", None)
        new_weight = request.form.get("edit-weight", None)

        # if input value passed is new and not empty update relevant column
        if new_first_name != profile["first_name"] and new_first_name != "":
            db.execute("UPDATE OR IGNORE user SET first_name = ? WHERE id = ?;", new_first_name, user_id)

        if new_last_name != profile["last_name"] and new_last_name != "":
            db.execute("UPDATE OR IGNORE user SET last_name = ? WHERE id = ?;", new_last_name, user_id)

        if new_date_of_birth != profile["date_of_birth"] and new_date_of_birth != "":
            db.execute("UPDATE OR IGNORE user SET date_of_birth = ? WHERE id = ?;", new_date_of_birth, user_id)

        if new_height != profile["height"] and new_height != "":
            db.execute("UPDATE OR IGNORE user SET height_cm = ? WHERE id = ?;", new_height, user_id)

        if new_weight != profile["weight"] and new_weight != "":
            db.execute("UPDATE OR IGNORE user SET weight_kg = ? WHERE id = ?;", new_weight, user_id)

        return redirect(url_for("profile"))

    return render_template("editprofile.html", profile_data=profile)


@app.route("/editworkout", methods=["GET", "POST"])
@login_required
def editworkout():
    user_id = session.get("user_id", None)
    workout_id = session.get("workout_id", None)

    # profile details from SQL db
    profile = db.execute("""
                            SELECT u.id id, username, first_name, last_name, date_of_birth, 
                            member_since, height_cm, weight_kg, w.unit weight_unit, t.time_system time_system 
                            FROM user u
                            JOIN weight_unit w ON u.weight_unit = w.id
                            JOIN time_system t ON u.time_system = t.id
                            WHERE u.id=?;
                        """, user_id)[0]

    # get workout data from SQL db
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
                new_date = request.form.get("editworkout-date", None)
                new_start_time = request.form.get("editworkout-start-time", None)
                new_end_time = request.form.get("editworkout-end-time", None)

                db.execute("UPDATE workout SET date = ?, start_time = ?, end_time = ? WHERE id = ?;", new_date, new_start_time, new_end_time, workout_id)
            
            except Exception as e:
                print(f"Exception editing date and time: {e}")
                return error_message("Oops, something went wrong...", 400)
            
        # delete set
        elif "delete-user-id" in request.form:
            try:
                user_id = request.form.get("delete-user-id", None)
                workout_id = request.form.get("delete-workout-id", None)
                exercise_id = request.form.get("delete-exercise-id", None)
                exercise_set = request.form.get("delete-exercise-set", None)

                db.execute("DELETE FROM workout_set WHERE user_id = ? AND workout_id = ? AND exercise_id = ? AND exercise_set = ?;", user_id, workout_id, exercise_id, exercise_set)

            except Exception as e:
                print(f"Exception deleting set: {e}")
                return error_message("Oops, something went wrong...", 400)

        # edit set
        elif "edit-user-id" in request.form:
            try:
                user_id = request.form.get("edit-user-id", None)
                workout_id = request.form.get("edit-workout-id", None)
                exercise_id = request.form.get("edit-exercise-id", None)
                exercise_set = request.form.get("edit-exercise-set", None)
                new_reps = request.form.get("edit-reps", None)
                new_weight = request.form.get("edit-weight", None)

                if profile.get("weight_unit", None) == 'lbs':
                    new_weight = lbs_kg_conversion(float(new_weight))

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
                user_id = request.form.get("add-user-id", None)
                workout_id = request.form.get("add-workout-id", None)
                exercise_id = request.form.get("add-exercise-id", None)
                add_set = request.form.get("add-set", None)
                add_reps = request.form.get("add-reps", None)
                add_weight = request.form.get("add-weight", None)

                if profile.get("weight_unit", None) == 'lbs':
                    add_weight = lbs_kg_conversion(float(add_weight))

                db.execute("INSERT OR IGNORE INTO workout_set (user_id, workout_id, exercise_id, exercise_set, reps, weight_kg) VALUES(?, ?, ?, ?, ?, ?);", user_id, workout_id, exercise_id, add_set, add_reps, add_weight)

            except Exception as e:
                print(f"Exception adding set to existing exercise: {e}")
                return error_message("Oops, something went wrong...", 400)

        # log new set
        else:
            try:
                weight = request.form.get("weight", None)
                reps = request.form.get("reps", None)
                exercise_set = request.form.get("set", None)
                exercise_name = request.form.get("exercise", None)
                exercise_id = db.execute("SELECT id FROM exercise WHERE name = ?;", exercise_name)[0].get("id", None)

                if profile.get("weight_unit", None) == 'lbs':
                    weight = lbs_kg_conversion(float(weight))

                # insert row into workout_set table
                db.execute("INSERT OR IGNORE INTO workout_set (user_id, workout_id, exercise_id, exercise_set, reps, weight_kg) VALUES (?, ?, ?, ?, ?, ?);", user_id, workout_id, exercise_id, exercise_set, reps, weight)

            except Exception as e:
                print(f"Exception logging new set: {e}")
                return error_message("Invalid exercise name.", 400)

        return redirect(url_for("editworkout"))

    return render_template("editworkout.html", sets=sets, workout_exercises=workout_exercises, workout_info=workout_info, profile_data=profile)


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session.get("user_id", None)
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
            workout_id = request.form.get("edit-workout-id", None)
            session["workout_id"] = workout_id

            return redirect(url_for("editworkout"))

    return render_template("index.html", workout_history=workout_history, dashboard=dashboard)


@app.route("/login", methods=["GET", "POST"])
def login():
    # clear session, if login request received
    if request.method == "POST":
        session.clear()

        # user details, retrieved from database
        request_username = request.form.get("username", None)
        user = retrieve_user(db, request_username)

        # check user info exists
        if user == None:
            return error_message("Invalid user name or password.", 403)

        # compare user password with received password via check_password_hash(hashed_password, plain_text_password).
        # if password incorrect, return error message
        if not check_password_hash(user.get("password_hash", None), request.form.get("password", None)):
            return error_message("Invalid user name or password.", 403)

        # if username and password pass, save user id and username to session
        session["user_id"] = user.get("id", None)
        session["user_name"] = user.get("username", None)

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
    user_id = session.get("user_id", None)

    # JOIN with weight_unit and time_system tables to display foreign key values
    profile = db.execute("""
                            SELECT u.id id, username, first_name, last_name, date_of_birth, 
                            member_since, height_cm, weight_kg, w.unit weight_unit, t.time_system time_system 
                            FROM user u
                            JOIN weight_unit w ON u.weight_unit = w.id
                            JOIN time_system t ON u.time_system = t.id
                            WHERE u.id=?;
                        """, user_id)[0]

    # post request - change weight unit
    if request.method == "POST":
        if "kg" in request.form:
            weight_unit = "kg"
            weight_unit_id = db.execute("SELECT id FROM weight_unit WHERE unit=?;", weight_unit)[0]["id"]
            db.execute("UPDATE OR IGNORE user SET weight_unit=? WHERE id=?;", weight_unit_id, user_id)

            return redirect(url_for("profile"))

        if "lbs" in request.form:
            weight_unit = "lbs"
            weight_unit_id = db.execute("SELECT id FROM weight_unit WHERE unit=?;", weight_unit)[0]["id"]
            
            db.execute("UPDATE OR IGNORE user SET weight_unit=? WHERE id=?;", weight_unit_id, user_id)

            return redirect(url_for("profile"))               

    return render_template("profile.html", profile_data=profile)


@app.route("/register_login", methods=["GET", "POST"])
def register_login():

    # post form - login details and email
    if request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        password_confirmation = request.form.get("password_confirmation", None)
        email = request.form.get("email", None)
 
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
        session["user_id"] = user.get("id", None)
        session["user_name"] = user.get("username", None)

        # redirect to register details page.
        return redirect(url_for("register_details"))

    return render_template("register_login.html")

@app.route("/register_details", methods=["GET", "POST"])
def register_details():

    print(f"PRINT USER ID: {session.get('user_id', None)}")

    # post form - profile details
    if request.method == "POST":
        user_id = session.get("user_id", None)
        first_name = request.form.get("firstname", None)
        last_name = request.form.get("lastname", None)
        date_of_birth = request.form.get("date-of-birth", None)
        height = request.form.get("height", None)
        weight = request.form.get("weight", None)

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

@app.route("/workoutanalytics", methods=["GET", "POST"])
@login_required
def workoutanalytics():
    # ============================= WIP - PLOTLY GRAPH =============================

    user_id = session.get("user_id", None)

    data_sets = db.execute("""
                           WITH set_data AS (
                                        SELECT w.date date, e.name exercise, MAX(ws.weight_kg) weight_kg
                                        FROM workout_set ws      
                                        JOIN exercise e ON ws.exercise_id = e.id
                                        JOIN workout w ON ws.workout_id = w.id
                                        WHERE ws.user_id = ?
                                        GROUP BY date, exercise 
                           )     
                           
                           SELECT * FROM set_data;
                            """, user_id)

    df_sets = pd.DataFrame(data_sets)

    fig_sets = px.line(df_sets, x='date', y='weight_kg', color='exercise', markers='true')
    
    plotly_jinja_data = {"fig_sets": fig_sets.to_html(full_html=False)}

    # pass dictionary into render_template, with dictionary with dashboard data as key value pairs?
    return render_template("workout_analytics.html", plotly_jinja_data=plotly_jinja_data)



@app.route("/workouthistory", methods=["GET", "POST"])
@login_required
def workouthistory():
    user_id = session.get("user_id", None)

    # pagination - workout history, showing 10 workouts per page
    workouts_sum = db.execute("SELECT COUNT() sum FROM workout WHERE user_id = ?;", user_id)[0].get("sum", None)
    workouts_per_page = 10
    number_of_pages = math.ceil(workouts_sum / workouts_per_page)
    pages = list(range(1, number_of_pages + 1))

    # if "workout_history_page" cookie is undefined, then set it to page 1
    if session.get("workout_history_page", None) == None:
        session["workout_history_page"] = 1

    current_page = session.get("workout_history_page", None)
    row_num_start = (current_page - 1) * workouts_per_page
    row_num_end = current_page * workouts_per_page

    # if session["workout_history_date_order_switch"] is None, set it to "DESC" order by default:
    if session.get("workout_history_date_order_switch", None) == None:
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
            workout_id = request.form.get("delete-workout-id", None)
            db.execute("DELETE FROM workout WHERE user_id=? AND id=?", user_id, workout_id)

            return redirect(url_for("workouthistory"))

        if "edit-workout-id" in request.form:
            workout_id = request.form.get("edit-workout-id", None)
            session["workout_id"] = workout_id

            return redirect(url_for("editworkout"))

        if "prev-page" in request.form:
            prev_page = session.get("workout_history_page", None) + int(request.form.get("prev-page", None))
            if prev_page >= 1:
                session["workout_history_page"] = prev_page

                return redirect(url_for("workouthistory"))

        if "next-page" in request.form:
            next_page = session.get("workout_history_page", None) + int(request.form.get("next-page", None))
            if next_page <= number_of_pages:
                session["workout_history_page"] = next_page

                return redirect(url_for("workouthistory"))

        if "change-page" in request.form:
            page = int(request.form.get("change-page", None))
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

# ===================================================== REST API ===================================================== 
# methods defaults to "GET"
@app.route("/exercise")
@login_required
def search_exercise():

    # query db for exercises containing name
    output = db.execute("""SELECT name FROM exercise LIMIT 300;""")
    
    # return json array of objects 
    # python dictionaries are json-serialized by default
    return output
    
    
