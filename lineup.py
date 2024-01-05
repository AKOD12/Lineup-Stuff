import pandas as pd
import numpy as np
import re
import plotly.figure_factory as ff
import os

# Define a function to sort the contents of each cell numerically
def sort_cell_contents(cell):
    if isinstance(cell, str):
        items = [x.strip() for x in cell.split(',')]
        items.sort(key=lambda x: int(re.search(r'\d+', x).group()))
        return ', '.join(items)
    else:
        return cell

# Define a function to calculate points based on the 'Result' value
def calculate_points(result):
    if result in ['O3', 'O3F']:
        return 3
    elif result in ['O2', 'O2F']:
        return 2
    elif result == 'FT - MK':
        return 1
    return 0

# Function to count the shots
def count_shots(result):
    return 1 if result in ['O2', 'O3', 'X2', 'X3', 'X3F', 'X2F', 'TO'] else 0

# Function to identify turnovers
def count_turnovers(result):
    return 1 if result == 'TO' else 0

# Function to count field goals made
def count_field_goals_made(result):
    return 1 if result in ['O2', 'O3', 'O2F', 'O3F'] else 0

# Function to count total field goals attempted
def count_field_goals_attempted(result):
    return 1 if result in ['O2', 'O3', 'X2', 'X3', 'O2F', 'O3F'] else 0

# Function to count three-pointers made
def count_three_point_made(result):
    return 1 if result in ['O3', 'O3F'] else 0

# Function to count total three-pointers attempted
def count_three_point_attempted(result):
    return 1 if result in ['O3', 'X3', 'O3F'] else 0

# Function to count free throws made
def count_free_throws_made(result):
    return 1 if result == 'FT - MK' else 0

# Function to count free throws attempted
def count_free_throws_attempted(result):
    return 1 if result in ['FT - MK', 'FT - MI'] else 0

# Function to count our offensive rebounds
def count_our_offensive_rebounds(result):
    return 1 if result == 'GT Off Reb' else 0

# Function to count opponent's offensive rebounds
def count_opponent_offensive_rebounds(result):
    return 1 if result == 'Opp Off Reb' else 0

# Import CSV files from folder and calculate lineup frequencies
folder_path = 'game-csv-2023'  # Update for the year of interest
dataframes = []

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        df['ON COURT'] = df['ON COURT'].apply(sort_cell_contents)
        df['Points'] = df['Result'].apply(calculate_points)
        df['Shots'] = df['Result'].apply(count_shots)
        df['Turnovers'] = df['Result'].apply(count_turnovers)
        df['FG Made'] = df['Result'].apply(count_field_goals_made)
        df['FG Attempted'] = df['Result'].apply(count_field_goals_attempted)
        df['3P Made'] = df['Result'].apply(count_three_point_made)
        df['3P Attempted'] = df['Result'].apply(count_three_point_attempted)
        df['FT Made'] = df['Result'].apply(count_free_throws_made)
        df['FT Attempted'] = df['Result'].apply(count_free_throws_attempted)
        df['Our Off Reb'] = df['Result'].apply(count_our_offensive_rebounds)
        df['Opp Off Reb'] = df['Result'].apply(count_opponent_offensive_rebounds)
        dataframes.append(df)

# Combine all games into one DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)

# Import CSV files from folder and calculate lineup frequencies
folder_path = 'game-csv-2023'  # Update for the year of interest
dataframes = []

for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        df['ON COURT'] = df['ON COURT'].apply(sort_cell_contents)
        df['Points'] = df['Result'].apply(calculate_points)
        df['Shots'] = df['Result'].apply(count_shots)
        df['Turnovers'] = df['Result'].apply(count_turnovers)
        df['FG Made'] = df['Result'].apply(count_field_goals_made)
        df['FG Attempted'] = df['Result'].apply(count_field_goals_attempted)
        df['3P Made'] = df['Result'].apply(count_three_point_made)
        df['3P Attempted'] = df['Result'].apply(count_three_point_attempted)
        df['FT Made'] = df['Result'].apply(count_free_throws_made)
        df['FT Attempted'] = df['Result'].apply(count_free_throws_attempted)
        df['Our Off Reb'] = df['Result'].apply(count_our_offensive_rebounds)
        df['Opp Off Reb'] = df['Result'].apply(count_opponent_offensive_rebounds)
        dataframes.append(df)

# Combine all games into one DataFrame
combined_df = pd.concat(dataframes, ignore_index=True)
