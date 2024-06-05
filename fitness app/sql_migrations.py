import csv
from cs50 import SQL


# ------------------------------------------------ import exercise_muscle_group.csv ------------------------------------------------

# db = SQL("sqlite:///fitnessapp.db")

# with open('exercise_muscle_group.csv', 'r') as f:
#     reader = csv.reader(f)
#     columns = next(reader)
#     query = 'INSERT OR IGNORE INTO exercise_muscle_group ({0}) VALUES ({1});'
#     query = query.format(','.join(columns), ','.join('?' * len(columns)))

#     for data in reader:
#         print(f"Loading: {data}")
#         db.execute(query, data[0], data[1])

#     print(f"Import csv into SQL db complete!")
# ------------------------------------------------ import exercise.csv ------------------------------------------------

# db = SQL("sqlite:///fitnessapp.db")

# with open('exercise.csv', 'r') as f:
#     reader = csv.reader(f)
#     columns = next(reader)
#     query = 'INSERT OR IGNORE INTO exercise ({0}) VALUES ({1});'
#     query = query.format(','.join(columns), ','.join('?' * len(columns)))

#     for data in reader:
#         print(f"Loading: {data}")
#         db.execute(query, data[0], data[1], None if data[2] == 'NULL' else data[2])
    

# ------------------------------------------------ import muscle_group.csv ------------------------------------------------

# db = SQL("sqlite:///fitnessapp.db")

# with open('muscle_group.csv', 'r') as f:
#     reader = csv.reader(f)
#     columns = next(reader)
#     query = 'INSERT INTO muscle_group ({0}) VALUES ({1});'
#     query = query.format(','.join(columns), ','.join('?' * len(columns)))
#     for data in reader:
#         db.execute(query, data)

# ------------------------------------------------ USER MIGRATION 3 ------------------------------------------------

# # TODO: create sqlite3 database connection
# db = SQL("sqlite:///fitnessapp.db")

# # TODO: create temp user table
# db.execute("""
#             CREATE TABLE IF NOT EXISTS temp_users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                 username TEXT UNIQUE NOT NULL,
#                 hash TEXT NOT NULL,
#                 member_since TEXT DEFAULT CURRENT_DATE,
#                 first_name TEXT,
#                 last_name TEXT,
#                 date_of_birth TEXT,
#                 age INTEGER,
#                 height_cm REAL,
#                 weight_kg REAL
#             );
# """)

# print("Created new table: temp_users")

# # TODO: migrate data from users table to temp users table
# users_rows = db.execute("SELECT * FROM users;")

# print("Loading table data: users...")

# for row in users_rows:
#     username = row.get("username")
#     hash = row.get("hash")
#     first_name = row.get("first_name")
#     last_name = row.get("last_name")
#     date_of_birth = row.get("date_of_birth")
#     member_since = row.get("member_since")
#     weight = row.get("weight_kg")
#     height = row.get("height_cm")
#     age = row.get("age")

#     db.execute("""
#                 INSERT OR IGNORE INTO temp_users
#                 (username, hash, first_name, last_name, date_of_birth, member_since, weight_kg, height_cm, age)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
#     """, username, hash, first_name, last_name, date_of_birth, member_since, weight, height, age)

#     print(f"Migrated user: {username} from users to temp_users.")

# # TODO: delete old users table
# db.execute("DROP TABLE IF EXISTS users;")

# print("Deleted old table: users.")

# # TODO: create new users table with modified fields
# db.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                 username TEXT UNIQUE NOT NULL,
#                 hash TEXT NOT NULL,
#                 member_since TEXT DEFAULT CURRENT_DATE,
#                 first_name TEXT,
#                 last_name TEXT,
#                 date_of_birth TEXT,
#                 height_cm REAL,
#                 weight_kg REAL
#             );
# """)

# print("Created new table: users")

# # TODO: load temp users data
# temp_data = db.execute("SELECT * FROM temp_users;")

# print("Loading table data: temp users...")

# # TODO: insert temp users rows into new users table
# for row in temp_data:
#     # TODO: parse row data from temp users table
#     username = row.get("username")
#     hash = row.get("hash")
#     first_name = row.get("first_name")
#     last_name = row.get("last_name")
#     date_of_birth = row.get("date_of_birth")
#     member_since = row.get("member_since")
#     weight = row.get("weight_kg")
#     height = row.get("height_cm")

#     # TODO: insert rows into new users table
#     db.execute("""
#                 INSERT OR IGNORE INTO users
#                 (username, hash, first_name, last_name, date_of_birth, member_since, weight_kg, height_cm)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?);
#     """, username, hash, first_name, last_name, date_of_birth, member_since, weight, height)

#     print(f"Migrated user: {username} from temp_users to users.")

# # TODO: delete temp users table
# db.execute("DROP TABLE IF EXISTS temp_users;")

# # TODO: select all rows from new users table for print check
# new_users = db.execute("SELECT * FROM users;")

# print("Migration complete.\n")
# print(new_users)


# ------------------------------------------------ USER MIGRATION 2 ------------------------------------------------


# # TODO: create sqlite3 database connection
# db = SQL("sqlite:///fitnessapp.db")

# # TODO: create temp user table
# db.execute("""
#                 CREATE TABLE IF NOT EXISTS temp_users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                 username TEXT UNIQUE NOT NULL,
#                 hash TEXT NOT NULL,
#                 first_name TEXT,
#                 last_name TEXT,
#                 date_of_birth TEXT,
#                 member_since TEXT DEFAULT CURRENT_DATE
#             );
# """)

# print("Created new table: temp_users.")

# # TODO: migrate data from users table to temp users table
# users_rows = db.execute("""
#                         SELECT * FROM users;
# """)

# print("Loading users data...")

# for row in users_rows:
#     username = row.get("username")
#     hash = row.get("hash")
#     first_name = row.get("first_name")
#     last_name = row.get("last_name")
#     date_of_birth = row.get("date_of_birth")
#     member_since = row.get("member_since")

#     db.execute("""
#                 INSERT OR IGNORE INTO temp_users
#                 (username, hash, first_name, last_name, date_of_birth, member_since)
#                 VALUES (?, ?, ?, ?, ?, ?);
#     """, username, hash, first_name, last_name, date_of_birth, member_since)

#     print(f"Migrated {username} from users to temp users.")

# # TODO: delete old users table
# db.execute("""
#             DROP TABLE IF EXISTS users;
# """)

# print("Deleted old table: users.")

# # TODO: create new users table with added fields
# db.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                 username TEXT UNIQUE NOT NULL,
#                 hash TEXT NOT NULL,
#                 member_since TEXT DEFAULT CURRENT_DATE,
#                 first_name TEXT,
#                 last_name TEXT,
#                 date_of_birth TEXT,
#                 age INTEGER,
#                 height_cm REAL,
#                 weight_kg REAL
#             );
# """)

# print("Created new users table.")

# # TODO: load temp users data
# temp_data = db.execute("""
#                         SELECT * FROM temp_users;
# """)

# print("Loading temp users table data...")

# # TODO: insert temp users rows into new users table
# for row in temp_data:
#     # TODO: parse row data from temp users table
#     username = row.get("username")
#     hash = row.get("hash")
#     first_name = row.get("first_name")
#     last_name = row.get("last_name")
#     date_of_birth = row.get("date_of_birth")
#     member_since = row.get("member_since")

#     # TODO: insert rows into new users table
#     db.execute("""
#                 INSERT OR IGNORE INTO users
#                 (username, hash, first_name, last_name, date_of_birth, member_since)
#                 VALUES (?, ?, ?, ?, ?, ?);
#     """, username, hash, first_name, last_name, date_of_birth, member_since)

#     print(f"Migrated user: {username} from temp users to users.")

# # TODO: delete temp users table
# db.execute("""
#             DROP TABLE IF EXISTS temp_users;
# """)

# # TODO: select all rows from new users table for print check
# new_users = db.execute("SELECT * FROM users;")

# print("Migration complete.\n")
# print(new_users)


# ------------------------------------------------ USER MIGRATION 1 ------------------------------------------------


# # TODO: create sqlite3 database connection
# db = SQL("sqlite:///fitnessapp.db")

# # TODO: create temp user table
# db.execute("""
#             CREATE TABLE IF NOT EXISTS temp_users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                 username TEXT UNIQUE NOT NULL,
#                 hash TEXT NOT NULL,
#                 first_name TEXT,
#                 last_name TEXT,
#                 date_of_birth TEXT
#             );
# """)

# print("Created new table: temp_users.")

# # TODO: migrate data from users table to temp users table
# users_rows = db.execute("""
#                         SELECT * FROM users;
# """)

# print("Loading users data...")

# for row in users_rows:
#     username = row.get("username")
#     hash = row.get("hash")
#     first_name = row.get("first_name")
#     last_name = row.get("last_name")

#     db.execute("""
#                 INSERT OR IGNORE INTO temp_users
#                 (username, hash, first_name, last_name)
#                 VALUES (?, ?, ?, ?);
#     """, username, hash, first_name, last_name)

#     print(f"Migrated {username} from users to temp users.")

# # TODO: delete old users table
# db.execute("""
#             DROP TABLE IF EXISTS users;
# """)

# print("Deleted old users table.")

# # TODO: create new users table with modified fields
# db.execute("""
#             CREATE TABLE IF NOT EXISTS users (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                 username TEXT UNIQUE NOT NULL,
#                 hash TEXT NOT NULL,
#                 first_name TEXT,
#                 last_name TEXT,
#                 date_of_birth TEXT,
#                 member_since TEXT DEFAULT CURRENT_DATE
#             );
# """)

# print("Created new users table.")

# # TODO: load temp users data
# temp_data = db.execute("""
#                         SELECT * FROM temp_users;
# """)

# print("Loading temp users table data...")

# # TODO: insert temp users rows into new users table
# for row in temp_data:
#     # TODO: parse row data from temp users table
#     username = row.get("username")
#     hash = row.get("hash")
#     first_name = row.get("first_name")
#     last_name = row.get("last_name")

#     # TODO: insert rows into new users table
#     db.execute("""
#                 INSERT OR IGNORE INTO users
#                 (username, hash, first_name, last_name)
#                 VALUES (?, ?, ?, ?);
#     """, username, hash, first_name, last_name)

#     print(f"Migrated user: {username} from temp users to users.")

# # TODO: delete temp users table
# db.execute("""
#             DROP TABLE IF EXISTS temp_users;
# """)

# # TODO: select all rows from new users table for print check
# new_users = db.execute("SELECT * FROM users;")

# print("Migration complete.\n")
# print(new_users)

