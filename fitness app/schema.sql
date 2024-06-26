CREATE TABLE IF NOT EXISTS user (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	username TEXT UNIQUE NOT NULL,
	password_hash TEXT NOT NULL,
	member_since TEXT DEFAULT CURRENT_DATE,
	first_name TEXT,
	last_name TEXT,
	email TEXT,
	date_of_birth TEXT,
	height_cm REAL,
	weight_kg REAL,
	weight_unit INTEGER DEFAULT 1,
	time_system INTEGER DEFAULT 1,
	FOREIGN KEY (weight_unit) REFERENCES weight_unit (id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (time_system) REFERENCES time_system (id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workout (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	user_id INTEGER NOT NULL,
	date TEXT NOT NULL,
	start_time TEXT,
	end_time TEXT,
	name TEXT,
	note TEXT,
	FOREIGN KEY (user_id) REFERENCES user (id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS workout_set (
	user_id INTEGER NOT NULL,
	workout_id INTEGER NOT NULL,
	exercise_id INTEGER NOT NULL,
	exercise_set INTEGER NOT NULL,
	reps INTEGER NOT NULL,
	weight_kg REAL NOT NULL,
	PRIMARY KEY (user_id, workout_id, exercise_id, exercise_set),
	FOREIGN KEY (user_id) REFERENCES user(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (exercise_id) REFERENCES exercise(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (workout_id) REFERENCES workout(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS muscle_group (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS upper_lower (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS push_pull (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS exercise (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	name TEXT UNIQUE NOT NULL,
	upper_lower_id INTEGER NOT NULL,
	push_pull_id INTEGER,
	FOREIGN KEY (upper_lower_id) REFERENCES upper_lower(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (push_pull_id) REFERENCES push_pull(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

-- intermediate/junction/associative table to facilitate 
-- many-to-many relationship beteween exercise- and muscle_group tables
-- e.g.: one exercise can relate to many muscle groups and vice versa 
CREATE TABLE IF NOT EXISTS exercise_muscle_group (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	exercise_id INTEGER,
	muscle_group_id INTEGER,
	FOREIGN KEY (exercise_id) REFERENCES exercise(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (muscle_group_id) REFERENCES muscle_group(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS weight_unit (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	unit text
);

CREATE TABLE IF NOT EXISTS time_system (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	time_system text
);

-- SQL queries used in app logic
-- index.html filtering for average workout duration
WITH durations AS (
SELECT date, time(end_time, "-"||strftime('%H', start_time)||" hours", "-"||strftime('%M', start_time)||" minutes") workout_duration
FROM workouts
WHERE user_id=1
AND end_time IS NOT NULL
AND start_time IS NOT NULL)

SELECT AVG((strftime('%H', workout_duration)*60)+strftime('%M', workout_duration)) avg_workout_duration_min FROM durations;

-- index.html(draft) filtering for average workout duration
SELECT date, strftime('%H:%M:%S', end_time), time(start_time), time(end_time), time(end_time, "-"||strftime('%H', start_time)||" hours", "-"||strftime('%M', start_time)||" minutes")
FROM workouts
WHERE user_id=?
AND end_time IS NOT NULL
AND start_time IS NOT NULL;


-- index.html days since last workout
SELECT (JULIANDAY(date('now'))-JULIANDAY(date)) AS days_since_last_worktout FROM workouts WHERE user_id=? ORDER BY date DESC LIMIT 1;


-- index.html number of workouts in last 7 days
SELECT COUNT(*) AS workouts_last_7_days FROM workouts WHERE user_id=? AND date > DATE(JULIANDAY('now')-7);


--index.html number of workouts last 30 days
SELECT COUNT(*) AS workouts_last_30_days FROM workouts WHERE user_id=1 AND date > DATE(JULIANDAY('now')-30);
SELECT * FROM workouts WHERE user_id=1 AND date > DATE(JULIANDAY('now')-30);


-- index.html number of workouts last 90 days
SELECT COUNT(*) AS workouts_last_90_days FROM workouts WHERE user_id=1 AND date > DATE(JULIANDAY('now')-90);


-- index.html total training volume
SELECT SUM(reps*weight_kg) AS total_volume_lifted
FROM workout a
JOIN workout_set b ON a.id=b.workout_id
JOIN exercise c ON b.exercise_id=c.id
WHERE 1=1
AND a.user_id=1;


-- index.html workout history
SELECT * FROM workouts WHERE user_id=? ORDER BY date DESC, start_time DESC LIMIT 5;


-- workouthistory.html count workout rows of user
SELECT COUNT() FROM workouts WHERE user_id = ?;


-- workouthistory.html workout history
-- using ROW_NUMBER() for pagination
WITH t AS (
	SELECT ROW_NUMBER () OVER (ORDER BY date DESC) row_num,
	date,
	start_time,
	end_time
	FROM workouts
	WHERE user_id = ?
)

SELECT * FROM t WHERE row_num > ? AND row_num <= ?;


