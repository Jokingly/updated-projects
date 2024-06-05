import pandas as pd
import plotly.express as px

from cs50 import SQL

db = SQL("sqlite:///fitnessapp.db")
user_id = 1

# TODO: Add time filter? Last 7, 14, 30, 60, 90 days and all time

# total sets performed per muscle group, all time
# columns required: sets (group by muscle group), muscle group
data_muscle_group_set = db.execute("""
                                        WITH muscle_group_set AS (
                                            SELECT mg.name muscle_group, COUNT(*) OVER (PARTITION BY mg.name) sets, COUNT(*) OVER (PARTITION BY mg.name) * 1.0 / COUNT(*) OVER () * 100 percent_total
                                            FROM workout_set as ws
                                            JOIN exercise e ON ws.exercise_id = e.id
                                            JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                            JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                            WHERE ws.user_id = 1                                            
                                        )

                                        SELECT * FROM muscle_group_set GROUP BY muscle_group;
                                        """, user_id)

# top 10 exercises by sets, descending, include muscle group in layout
data_exercise_set = db.execute("""
                                WITH exercise_set AS (
                                    SELECT mg.name muscle_group, e.name exercise, COUNT(e.name) sets
                                    FROM workout_set as ws
                                    JOIN exercise e ON ws.exercise_id = e.id
                                    JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                    JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                    WHERE ws.user_id = 1
                                    GROUP BY exercise
                                    ORDER BY sets DESC
                                    LIMIT 10
                                )

                               SELECT * FROM exercise_set;
                                """)

# top 10 exercises by weight, descending, include muscle group in layout
data_exercise_weight = db.execute("""
                                WITH exercise_weight AS (
                                    SELECT mg.name muscle_group, e.name exercise, MAX(ws.weight_kg) OVER (PARTITION BY e.name) max_weight_kg
                                    FROM workout_set as ws
                                    JOIN exercise e ON ws.exercise_id = e.id
                                    JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                    JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                    WHERE ws.user_id = 1
                                )

                               SELECT * FROM exercise_weight GROUP BY exercise ORDER BY max_weight_kg DESC;
                                """)

# max weight lifted per exercise per workout
# ADD DROPDOWN FOR INTERACTIVE DATA ANALYSIS WITH FigureWidget
data_set = db.execute("""
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

df_sets = pd.DataFrame(data_set)

fig_sets = px.line(df_sets, x='date', y='weight_kg', color='exercise', markers='true')


# some sort of general data query
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



plotly_jinja_data = {"fig_sets": fig_sets.to_html(full_html=False)}




