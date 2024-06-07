import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from cs50 import SQL

db = SQL("sqlite:///fitnessapp.db")
user_id = 1

# TODO: Add time filter? Last 7, 14, 30, 60, 90 days and all time

# pie chart: sets performed per muscle group of all time
# sql columns: muscle_group, sets
sql_muscle_group_set = db.execute("""
                                        WITH muscle_group_set AS (
                                            SELECT mg.name muscle_group, COUNT(*) OVER (PARTITION BY mg.name) sets
                                            FROM workout_set as ws
                                            JOIN exercise e ON ws.exercise_id = e.id
                                            JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                            JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                            WHERE ws.user_id = 1                                            
                                        )

                                        SELECT * FROM muscle_group_set GROUP BY muscle_group;
                                        """, user_id)

# create pandas dataframe
df_muscle_group_set = pd.DataFrame(sql_muscle_group_set)

# create plotly graph objects pie chart
fig_muscle_group_pie = go.Figure()
fig_muscle_group_pie.add_trace(
    go.Pie(
        values=list(df_muscle_group_set.sets),
        labels=list(df_muscle_group_set.muscle_group),
        textinfo='percent+value',
        title='All Time Sets Per Muscle Group'
    )
)

# horizontal bar chart: top 10 exercises by sets, descending, include muscle group in layout
# sql columns: muscle_group, exercise, sets
sql_exercise_set = db.execute("""
                                WITH exercise_set AS (
                                    SELECT mg.name muscle_group, e.name exercise, COUNT(e.name) sets
                                    FROM workout_set as ws
                                    JOIN exercise e ON ws.exercise_id = e.id
                                    JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                    JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                    WHERE ws.user_id = 1
                                    GROUP BY exercise
                                    ORDER BY sets ASC
                                    LIMIT 10
                                )

                               SELECT * FROM exercise_set;
                                """)

# create pandas dataframe
df_exercise_set = pd.DataFrame(sql_exercise_set)

# create plotly graph objects horizontal bar chart



# horizontal bar chart: top 10 exercises by weight, descending, include muscle group in layout
# sql columns: muscle_group, exercise, max_weight_kg
# sql order by asc to show highest value at top of horizontal bar chart
sql_exercise_weight = db.execute("""
                                WITH exercise_weight AS (
                                    SELECT mg.name muscle_group, e.name exercise, MAX(ws.weight_kg) OVER (PARTITION BY e.name) max_weight_kg
                                    FROM workout_set as ws
                                    JOIN exercise e ON ws.exercise_id = e.id
                                    JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                    JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                    WHERE ws.user_id = 1
                                    LIMIT 10
                                )

                               SELECT * FROM exercise_weight GROUP BY exercise ORDER BY max_weight_kg ASC;
                                """)

# create pandas dataframe
df_exercise_weight = pd.DataFrame(sql_exercise_weight)

# create plotly graph objects horizontal bar chart



# scatter-/ line graph: max weight progression by exercise over workouts
# sql columns: date, exercise, weight_kg
# ADD DROPDOWN FOR INTERACTIVE DATA ANALYSIS WITH FigureWidget
sql_weight_progression = db.execute("""
                        WITH set_data AS (
                                    SELECT w.date date, mg.name muscle_group, e.name exercise, MAX(ws.weight_kg) weight_kg
                                    FROM workout_set ws      
                                    JOIN exercise e ON ws.exercise_id = e.id
                                    JOIN workout w ON ws.workout_id = w.id
                                    JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                    JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                    WHERE ws.user_id = ?
                                    GROUP BY date, exercise 
                        )     
                        
                        SELECT * FROM set_data;
                        """, user_id)

# create pandas dataframe
df_weight_progression = pd.DataFrame(sql_weight_progression)

# create plotly line graph
fig_weight_progression = px.line(df_weight_progression, x='date', y='weight_kg', color='exercise', markers='true')


# template query
general_query = db.execute("""
                                WITH general_table AS (
                                    SELECT mg.name muscle_group, COUNT(mg.name) sets
                                    FROM workout_set as ws
                                    JOIN exercise e ON ws.exercise_id = e.id
                                    JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                    JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                    WHERE ws.user_id = 1
                                    
                                )

                               SELECT * FROM general_table;
                                """)



plotly_jinja_data = {"fig_weight_progression": fig_weight_progression.to_html(full_html=False), "fig_muscle_group_pie": fig_muscle_group_pie.to_html(full_html=False)}




