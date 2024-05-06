# IronMetrics

Video Demo: https://youtu.be/zgJ8W3RJBmo

Description: IronMetrics is a fitness app that allows users to create profiles to track their workouts and see analytics about their workout habits. It is a web app that that uses a SQLite3 database to perform create, read, update and delete (CRUD) functionalities on user data.

## Features

Below is a list with brief explanations of the app's features:
- New account registeration
    - Users can create a new account by filling out the required fields of username, password and confirm password
    - Password must contain one special character, one number, one upper case letter and one lower case letter
- User login
    - Users can login with their username and password to use track their workouts
- Edit profile information
    - Shows profile information
    - First name, last name, date of birth, height(cm) and weight(kg) can be updated
    - Change password button, allows password to be modified
- Change password
    - Users can change their password, by confirming the old password, entering a new password and confirming the new password
- Homepage
    - Logged-in users are redirected to the homepage
    - A workout metrics dashboard is located near the top
    - Below the workout dashboard is a brief workout history, showing the 5 most recent workouts that can be edited or deleted
- Create workouts
    - Users can create workout records to track exercises, sets, reps and weights performed
    - The pre-populated workout date and start time can be edited
    - To create an exercise set, the exercises must be chosen from the autosuggest field that appears when typing an exercise name
    - Clicking on one of the autosuggstions will populated the exercise input field with the autosuggestion
    - Incorrectly entered exercises will raise an error
    - Sets, reps and weights can also be entered
    - Exercises cannot have duplicate sets in the same workout
    - Exercise sets can be deleted to make corrections
- Workout history
    - Users can view, edit and delete all their workouts
    - The pagination shows 10 workouts per page
    - Workouts are sorted by date in descending order by default, meaning the most recent workout comes first and the oldest workout comes last
    - The button next to the date heading switches the workout date sorting between ascending and descending orders

<br>

## Tech Stack

The tech stack for IronMetrics includes:
- Bootstrap
- CSS
- Flask
- HTML
- JavaScript
- Python
- SQLite3

For the frontend, IronMetrics primarily relies on Bootstrap's pre-built components, in SCSS, HTML and JavaScript, for UI-/UX design and -functionality. CSS was used to further customise certain elements. Further frontend functionality was built with JavaScript, as needed. The web pages were designed, structured and displayed with HTML.
The minimalistically-designed UI's color palette primarily uses green, from Bootstrap's success class, and white. Text color is black on white background or white on green background. Plotly and SCSS were also considered for the frontend.

For the backend, Flask and Python are used as the web development framework and programming language, respectively. SQLite3 serves as the database, as it is easy to set up and includes CRUD and other necessary features to support the web app features. PostgreSQL, MySQL and SQLAlchemy were also considered for the project.

<br>

## App folder structure

IronMetrics follows Flask's default folder structure:
- finalproject
    - flask_session
    - static
    - templates

### finalproject

finalproject is the parent folder, also known as project root, containing all project resources.

### flask_session

flask_session is used to temporarily store session (cookie) data on the server-side. A session is measured as the period of time, when a client logs into the server and logs out of the server. Information including user ID and relevant app data are gathered during this period. Session data can be used to transfer information between web pages and features. Storing the session on the server-side has security advantages, as the data cannot be altered or tampered with.

### static

The static folder is used to store and serve static files. Static files do not change when the web server is running and are not generated with code while executing the program. This means that they do not change from one request to another. Examples of static files include CSS, JavaScript and images.

### templates

This project's templates are HTML files containing both static- and dynamic elements.

<br>

## Files

The above-mentioned folders contain the following files:

- finalproject
    - app.py
    - fitnessapp.db
    - helpers.py
    - loadexercisedata.py
    - readme.md
    - schema.sql
    - usersmigration.py
- flask_session (stores flask session data)
- static
    - scripts.js
- templates
    - base.html
    - changepassword.html
    - createworkout.html
    - editprofile.html
    - editworkout.html
    - error_message.html
    - index.html
    - login.html
    - profile.html
    - register.html
    - workouthistory.html

### finalproject files:

#### app.py

This is the main Python file containing the backend logic of the web app. The functions are ordered by their name in alphabetical order from A-Z in the file.

**after_request**

This function is not linked to an HTML file and was referenced from CS50's problem set 9 - Finance.
It modifies key-value pairs in response.headers to not cache HTML responses.

**changepassword (login required)**

Renders the changepassword.html file, and updates the relevant user's password, if it meets set requirements. A new password must have at least one lower case letter, one upper case letter, one number and one special symbol.
An if statement is used to check that a new password meets set requirements. The new password and confirm password need to match, to change the password.

It is worth noting that the user is able to change their password to an old password that was used in the past, as long as it matches the character requirements. Requiring passwords to contain a minimum length is a security best practice that can be implemented.

**createworkout (login required)**

This file renders the creatworkout.html template. This function allows users to create a new workout record in the SQLite3 database (database) table "workouts".
session["workout_id"] is cleared with session.pop("workout_id", None). This way, if session["workout_id"] does not exist, None is returned, instead of raising an error.
Once session["workout_id"] is cleared, a new workout record is created in the database table "workouts", of which the new workout id is set as session["workout_id"]'s value.
The user is then redirected to editworkout.html.

**editprofile (login required)**

User data is queried from the database table "users" and displayed on the page. This includes first name, last name, date of birth, height(cm) and weight(kg). New values for the relevant fields can be submitted via a POST request form. Upon submission of new values, the relevant user record in the database table "users" will be updated accordingly.

**editworkout (login required)**

Linked to the editworkout.html file, this function updates workout information, deletes and updates exercise records.
session.get("user_id") and session.get("workout_id") are used to filter for the relevant workout record. It is then shown on the page and can be edited. Changeable elements include date, start time, end time and workout sets, which include exercise, set, reps and weight. Try- and except clauses are used to catch expected- and unexpected errors. Workout exercises and sets are grouped by exercise name and set number, both in ascending order. This ensures a structured overview of the data, regardless of order in which the exercise and sets were entered.

**index (login required)**

This function renders the index.html file, showing the workout metrics dashboard and brief workout history.
The workout metrics dashboard uses the user id to query the database and calculate various metrics. This includes average workout duration, days since last workout, workouts in last 7 days, workouts in last 30 days, workouts in last 90 days and total volume lifted. Days since last workout uses a try- and except clause to catch an error that is raised, when a user account has no workout records. The total volume lifted calculation also uses a try- and except clause for a similar reason.
The data is loaded into a dictionary called "dashboard" and passed into the render_template function, as one variable with many key-value pairs, to simplify passing multiple variables at once.

The brief workout history shows the 5 most recent workouts that can be deleted or edited.

**login**

Linked to the login.html file, this functions allows the user to login to their profile. The user id and password is submitted via a post request form. Upon successful validation of both inputs, with the retrieve_user- and check_password_hash functions, the user is then redirected to index.html. Errors are raised with the error_message function with a relevant message.

**logout (login required)**

This function is related to the base.html file. Specifically, the logout button located in the top right corner of the navigation bar, when a user is logged in. When executed it logs out the user from their session with session.pop("user_id", None) and redirects them to login.html.

**profile (login required)**

This function renders the profile.html file. The page displays profile information including user id, username, first name, last name, date of birth, member since, height(cm) and weight(cm) and features an edit profile button. The information is queried from the database table "users" with the user id.

**register**

Linked to the register.html file, this function allows users to create a new account to use the web app, via a post request form. The username, password and confirm password fields are required, in order to create an account. First name, last name, date of birth, height(cm) and weight(kg) are optional fields. They can be edited later in the profile page. If-statements are used to check that password and confirm password match, the username does not already exist in the database and that the password meets security requirements.

**workouthistory (login required)**

This function shows the user all workouts ever created in their account. The user id is used to filter the relevant workout records from the database table "workouts". Workout records are paginated to 10 rows per page. The user can navigate between previous, next and specific pages to view their workout history. The pagination feature is manually built with SQLite3. The SQLite3 function ROW_NUMBER () is used to number and filter the rows returned. SQLAlchemy offered built-in pagination, which could have streamlined the implementation of this feature. However, implementing SQLAlchemy would have required all SQLite3 queries to be rewritten, which was decided against for this project. The workout history is sorted by date in descending order by default and can be sorted by date in ascending order with the button next to the table heading date. The sorting can be switched back and forth with the button. Users can also edit and delete workout records on this page.

<br>

#### fitnessapp.db

This is the web app's SQLite3 database file. The relational tables are designed to minimise column redundancy. The web app's various features perform CRUD (Create, Read, Update & Delete) on this database. Examples include user profile creation, updating user profiles, reading workout history, editing workouts, deleting workouts, etc.

fitnessapp.db contains the following tables, columns and data types:

- exercises
    - id INTEGER (primary key)
    - exercise TEXT
- sets
    - user_id INTEGER (foreign key referencing the user table's id column)
    - workout_id INTEGER (foreign key referencing the workout table's id column)
    - exercise_id INTEGER (foreign key referencing the exercise table's id column)
    - exercise_set INTEGER
    - reps INTEGER
    - weight_kg REAL
    - PRIMARY KEY (user_id, workout_id, exercise_id, exercise_set)
- users
    - id INTEGER (primary key)
    - username TEXT
    - hash TEXT
    - member_since TEXT
    - first_name TEXT
    - last_name TEXT
    - date_of_birth TEXT
    - height_cm REAL
    - weight_kg REAL
- workouts
    - id INTEGER
    - user_id INTEGER (foreign key referencing the user table's id column)
    - date TEXT
    - start_time TEXT
    - end_time TEXT

<br>

#### helpers.py

helpers.py contains support functions that are imported in app.py for reuse. This facilitates the DRY (Don't Repeat Yourself) principle. Functions in this file are referenced from CS50's problem set 9 - Finance.

helpers.py includes the following functions:
- error_message(message, code=400)

    Takes in error message- and code arguments. The default code is 400, if no code is provided. It renders an error page showing a meme with the error message- and code arguments.

- login_required(f)

    A function decorator, requiring users to be logged in to access the wrapped function. Otherwise, they will be redirected to the login page. The wrapped functions are usually functions that render html files.

- retrieve_user(database, username_form_id)

    This function takes a database variable and string as arguments, respectively. Returns a user dict from the database table "users". Returns None if the user does not exist.

<br>

#### loadexercisedata.py

This Python file performs an API call to an open source workout exercises database at https://wger.de/api/v2/ by https://wger.de/en/software/api.
The JSON data is parsed and loaded into the SQLite3 database fitnessapp.db.

<br>

#### readme.md

A documentation file containing instructions, support or details to help readers better undertand a project. It is formatted in the lightweight markup language Markdown.

<br>

#### schema.sql

This file contains the SQL queries used to create the tables in fitnessapp.db and to facilitate the interactions between the web app and the database.
It includes statements to create the database tables "users", "workouts", "sets" and "exercises".
There are also statements querying data to be displayed on pages, such as on index.html and workouthistory.html. Example metrics include average workout duration, days since last workout, workouts in last 7 days, workouts in last 30 days, workouts in last 90 days, total training volume, workout history, workout history pagination and sorting workout history by date.

<br>

#### usersmigration.py

This Python file was used to update the database table "users", while preserving the existing data. This was used to modify the database "users" table a number of times.
The process includes the following steps:
- migrate the existing data from the old table to a temporary table
- delete the old table
- create a new table
- migrate data from the temporary table to the new table
- delete the temporary table.

<br>

### flask_session files:

This folder stores auto-generated files with user session data. A session is measured as the period of time, when a client logs into the server and logs out of the server.

<br>

### static files:

#### scripts.js

This file contains JavaScript code to extend the frontend functionality of the web app.

It includes functions for the following pages:
- createworkout.html - prepopulate date- and time input fields
- editworkout.html - autosuggestions for exercise input box from https://wger.de/api/v2/exercise/${parameters} with parameters ?language=2&is_main=False&ordering=name&limit=400
- editworkout.html - click autosuggestions to populate exercise input box
- editworkout.html - redundant code for hiding/showing input fields to edit workout date, start time and end time

<br>

### templates files:

This folder contains HTML template files that containt static- and dynamic content. The Jinja templating language is used to write dynamic and easy-to-maintain HTML pages. Bootstrap classes are used to add UI design and frontend functionality.

#### base.html

The base.html file serves as the boilerplate code, containing sections of code that is repeated across multiple files.
These include the doctype declaration, head tag, body tag, navigation bar and footer tag.

#### changepassword.html

This HTML file contains a form that allows users to change their password.

#### createworkout.html

The createworkout.html file contains a pre-populated form that users can edit to create a workout record.

#### editprofile.html

This HTML file contains a form that lets users change their profile details, including first name, last name, date of birth, height(cm) and weight(kg).

#### editworkout.html

The editworkout.html file allows users to edit the workout information and exercises relating to a workout. The former includes, date, start time and end time. The latter includes exercises, sets, reps and weights(kg). Workout exercises and sets are grouped by exercise name and set number, both in ascending order. This ensures a structured overview of the data, regardless of order in which the exercise and sets were entered.

#### error_message.html

This HTML file displays a meme with a customisable error message and error code. It is referenced from CS50's problem set 9 - Finance.

#### index.html

The index.html file is the default page that a user is redirected to, after successful login.
It shows the users a workout metrics dashboard and a brief workout history containing the most recent 5 workouts.

#### login.html

This is the default page shown, if a user is not logged into the web app.
The user can login with their credentials or create a new account with the register button on the top right.

#### profile.html

This HTML file displays a users profile data, including user id, member since, username, first name, last name, date of birth, height(cm) and weight(kg).
The user can click on the edit profile button to update their details or the edit password button to change their password.

#### register.html

The register.html file allows users to enter information to create a new account that can be used to access the web app.
Username, password and confirm password are required fields for registration.
First name, last name, date of birth, height(cm) and weight(kg) are optional fields and can be updated after account creation through profile.html.

#### workouthistory.html

This HTML file shows the user a history of all the workouts ever created on their respective account. The records are ordered by date in descending order by default, which can be switched to ascending order by clicking on the button next to the date heading. Additionally, the workout data is paginated to 10 rows per page for a better viewing experience. Workout records can be edited or deleted from this page.

<br>

## Conclusion
Designing and implementing a full stack application from start to finish was a challenging and educational experience. The steps of this project followed broadly included ideation, define functionality, choose tech stack, implementing the front- and backend and repeating steps.

Some of the challenges encountered along the way are to reduce redundancy while designing a relational database, updating relational database tables, dealing with scope creep, troubleshooting unexpected problems, refactoring code, making tradeoffs and learning new technologies.

Overall, the CS50 final project was challenging and forced me to gain a better understanding of practical programming by selecting, learning and applying new technologies to bring an app idea to life.

