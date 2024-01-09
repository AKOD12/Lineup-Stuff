import streamlit as st
import pandas as pd
import os
import re

# Helper functions for specific calculations
def count_shots(result):
    return 1 if result in ['O2', 'O3', 'X2', 'X3', 'X3F', 'X2F', 'TO'] else 0

def calculate_points(result):
    if result in ['O3', 'O3F']:
        return 3
    elif result in ['O2', 'O2F']:
        return 2
    elif result == 'FT - MK':
        return 1
    return 0

def count_field_goals_made(result):
    return 1 if result in ['O2', 'O3', 'O2F', 'O3F'] else 0

def count_field_goals_attempted(result):
    return 1 if result in ['O2', 'O3', 'X2', 'X3', 'O2F', 'O3F'] else 0

def count_three_point_made(result):
    return 1 if result in ['O3', 'O3F'] else 0

def count_three_point_attempted(result):
    return 1 if result in ['O3', 'X3', 'O3F'] else 0

def count_free_throws_made(result):
    return 1 if result == 'FT - MK' else 0

def count_free_throws_attempted(result):
    return 1 if result in ['FT - MK', 'FT - MI'] else 0

def count_turnovers(result):
    return 1 if result == 'TO' else 0

def sort_cell_contents(cell):
    if isinstance(cell, str):
        items = [x.strip() for x in cell.split(',')]
        items.sort(key=lambda x: int(re.search(r'\d+', x).group()))
        return ', '.join(items)
    else:
        return cell

def calculate_plus_minus(offensive_stats, defensive_stats):
    offensive_stats.set_index('ON COURT', inplace=True)
    defensive_stats.set_index('ON COURT', inplace=True)
    plus_minus = offensive_stats['Points'] - defensive_stats['Points']
    offensive_stats.reset_index(inplace=True)
    defensive_stats.reset_index(inplace=True)
    return plus_minus

def process_stats(df, offense_or_defense):
    filtered_df = df[df['Row'] == offense_or_defense]
    filtered_df['Points'] = filtered_df['Result'].apply(calculate_points)
    filtered_df['Shots'] = filtered_df['Result'].apply(count_shots)
    filtered_df['Turnovers'] = filtered_df['Result'].apply(count_turnovers)
    filtered_df['FG Made'] = filtered_df['Result'].apply(count_field_goals_made)
    filtered_df['FG Attempted'] = filtered_df['Result'].apply(count_field_goals_attempted)
    filtered_df['3P Made'] = filtered_df['Result'].apply(count_three_point_made)
    filtered_df['3P Attempted'] = filtered_df['Result'].apply(count_three_point_attempted)
    filtered_df['FT Made'] = filtered_df['Result'].apply(count_free_throws_made)
    filtered_df['FT Attempted'] = filtered_df['Result'].apply(count_free_throws_attempted)
    filtered_df['Possessions'] = filtered_df['Shots'] + filtered_df['Turnovers']

    agg_functions = {
        'Points': 'sum',
        'Shots': 'sum',
        'Turnovers': 'sum',
        'FG Made': 'sum',
        'FG Attempted': 'sum',
        '3P Made': 'sum',
        '3P Attempted': 'sum',
        'FT Made': 'sum',
        'FT Attempted': 'sum',
        'Possessions': 'sum'
    }

    stats = filtered_df.groupby('ON COURT').agg(agg_functions).reset_index()

    stats['Points per Shot'] = (stats['Points'] / stats['Shots']).round(3)
    stats['FG%'] = (stats['FG Made'] / stats['FG Attempted']).round(3) * 100
    stats['3P%'] = (stats['3P Made'] / stats['3P Attempted']).round(3) * 100
    stats['FT%'] = (stats['FT Made'] / stats['FT Attempted']).round(3) * 100
    stats['Turnover Percentage'] = (stats['Turnovers'] / stats['Possessions']).round(3) * 100
    cols = ['ON COURT', 'Possessions', 'Points', 'Points per Shot', 
            'FG Made', 'FG Attempted', 'FG%', '3P Made', '3P Attempted', 
            '3P%', 'Turnovers', 'Turnover Percentage', 'FT Made', 
            'FT Attempted', 'FT%']

    stats = stats[cols]

    return stats

def load_and_process_data(selected_files):
    dataframes = []
    folder_path = 'game-csv-2023'
    for filename in selected_files:
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)
        df['ON COURT'] = df['ON COURT'].apply(sort_cell_contents)
        dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return process_stats(combined_df, 'OFFENSE'), process_stats(combined_df, 'DEFENSE'), combined_df

def get_password():
    try:
        with open("secrets.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None  # You can set a default password or handle this case as needed


# Streamlit app layout
st.markdown("Created by: Ankith Kodali (more commonly known as AK)")
# Get the password from the file
correct_password = get_password()
if correct_password is None:
    st.error("Password file not found. Please contact AK.")
    st.stop()

password = st.text_input("Enter password to access lineup data", type="password")

if password != correct_password:
    st.error("Incorrect password.")
    st.stop()


# Layout for GT logo and title
col1, col2 = st.columns([1, 4])

with col1:
    st.image('gtlogo.svg', width=120)

with col2:
    st.title('Lineup Analysis')  # App title

# Automatic listing of files in 'game-csv-2023' folder
try:
    files_with_extension = [f for f in os.listdir('game-csv-2023') if f.endswith('.csv')]
    files = [f[:-4] for f in files_with_extension]  # Remove the '.csv' from each filename
    selected_files_with_extension = st.multiselect('Select game for analysis:', files)
    selected_files = [f + '.csv' for f in selected_files_with_extension]  # Add back the '.csv' for processing
except Exception as e:
    st.error(f'Error accessing folder: {e}')

# Load data button
if st.button('Load Data'):
    if selected_files:
        try:
            offensive_stats, defensive_stats, combined_df = load_and_process_data(selected_files)
            st.session_state['offensive_stats'] = offensive_stats.sort_values('Possessions', ascending=False)
            st.session_state['defensive_stats'] = defensive_stats.sort_values('Possessions', ascending=False)
            st.session_state['combined_df'] = combined_df  # Save combined DataFrame in session state
            st.session_state['data_loaded'] = True
            st.success('Data loaded successfully')
        except Exception as e:
            st.error(f'An error occurred: {e}')
    else:
        st.error('No files selected. Please select files for analysis.')

# Display data based on user input
if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
    min_poss = st.number_input('Enter minimum possessions for lineups to display:', min_value=1, value=20)
    view_mode = st.radio("View Mode", ('Offensive Stats', 'Defensive Stats'))
    if view_mode == 'Offensive Stats':
        filtered_data = st.session_state['offensive_stats'][st.session_state['offensive_stats']['Possessions'] >= min_poss]
        filtered_data = filtered_data.sort_values('Possessions', ascending=False)
        st.dataframe(filtered_data.reset_index(drop=True))
    elif view_mode == 'Defensive Stats':
        filtered_data = st.session_state['defensive_stats'][st.session_state['defensive_stats']['Possessions'] >= min_poss]
        filtered_data = filtered_data.sort_values('Possessions', ascending=False)
        st.dataframe(filtered_data.reset_index(drop=True))
