import pandas as pd
import plotly.express as px

from cs50 import SQL

db = SQL("sqlite:///fitnessapp.db")

# WIP - WEIGHT PROGRESSION LINE CHART
# ADD DROPDOWN FOR INTERACTIVE DATA ANALYSIS WITH FigureWidget
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


# WIP - WHAT OTHER VALUES COULD BE USEFUL?
data_muscle_group = db.execute("""
                                with muscle_group_worked AS (
                                    SELECT mg.name muscle_group, COUNT(mg.name) sets
                                    FROM workout_set as ws
                                    JOIN exercise e ON ws.exercise_id = e.id
                                    JOIN exercise_muscle_group emg ON e.id = emg.exercise_id
                                    JOIN muscle_group mg ON emg.muscle_group_id = mg.id
                                    WHERE ws.user_id = 1
                                    GROUP BY muscle_group
                                )

                                """)




plotly_jinja_data = {"fig_sets": fig_sets.to_html(full_html=False)}




