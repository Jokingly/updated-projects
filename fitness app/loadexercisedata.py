import requests
import json

from cs50 import SQL

"""
WGER
API call to https://wger.de/api/v2/ by https://wger.de/en/software/api.
Populates exercises from fitnessapp.db with exercise names from above API.
"""

# create sqlite database connection
db = SQL("sqlite:///fitnessapp.db")

# print json object in formatted way
def jprint(object):
    # create formatted string of Python JSON object
    text = json.dumps(object, sort_keys=True, indent=4)
    print(text)

# store api urls
url = "https://wger.de/api/v2/"
exerciseurl = "https://wger.de/api/v2/exercise/"
exercisebaseurl = "https://wger.de/api/v2/exercise-base/"

# parameters to get English exercise names
parameters = {
    "language": 2,
    "is_main": False,
    "ordering": "name",
    "limit": 400
}

# response object from api call
response = requests.get(exerciseurl, params=parameters)

results = response.json()["results"]
exercises = list()

# add exercise names to exercises list
for result in results:
    name = result["name"].lower()
    # filter out names in language other than English
    if "\u00f3" in name or "maquina" in name or "jalon" in name or "gemelos" in name:
        continue
    exercises.append(name)

# loop through exercises list and add each exercise into the exercises table from fitnessapp.db
for exercise in exercises:
    # UNCOMMENT TO INSERT ROWS INTO exercises table FROM fitnessapp.db
    db.execute("INSERT OR IGNORE INTO exercises(exercise) VALUES (?)", exercise)
    print("Loaded:", exercise)

# print(response.status_code)
# jprint(exercises)

