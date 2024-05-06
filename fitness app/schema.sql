CREATE TABLE IF NOT EXISTS users (
          	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          	username TEXT UNIQUE NOT NULL,
          	hash TEXT NOT NULL,
			member_since TEXT DEFAULT CURRENT_DATE,
          	first_name TEXT,
          	last_name TEXT,
          	date_of_birth TEXT,
			height_cm REAL,
			weight_kg REAL
);

CREATE TABLE IF NOT EXISTS workouts (
          	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          	user_id INTEGER NOT NULL,
          	date TEXT NOT NULL,
          	start_time TEXT,
          	end_time TEXT,
          	FOREIGN KEY (user_id) REFERENCES users (id)
ON UPDATE CASCADE
ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS sets (
	user_id INTEGER NOT NULL,
	workout_id INTEGER NOT NULL,
	exercise_id INTEGER NOT NULL,
	exercise_set INTEGER NOT NULL,
	reps INTEGER NOT NULL,
	weight_kg REAL NOT NULL,
	PRIMARY KEY (user_id, workout_id, exercise_id, exercise_set),
	FOREIGN KEY (user_id) REFERENCES users(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (exercise_id) REFERENCES exercises(id)
	ON UPDATE CASCADE
	ON DELETE CASCADE,
	FOREIGN KEY (workout_id) REFERENCES workouts(id)
	ON UPDATE CASCADE
ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exercises (
          	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
          	exercise TEXT UNIQUE NOT NULL
);


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
FROM workouts a
JOIN sets b ON a.id=b.workout_id
JOIN exercises c ON b.exercise_id=c.id
WHERE a.user_id=?;


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


