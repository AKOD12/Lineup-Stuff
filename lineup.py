import streamlit as st
import pandas as pd
import os
import re

# Define your functions for data processing

def sort_cell_contents(cell):
    if isinstance(cell, str):
        items = [x.strip() for x in cell.split(',')]
        items.sort(key=lambda x: int(re.search(r'\d+', x).group()))
        return ', '.join(items)
    else:
        return cell

def calculate_points(result):
    if result in ['O3', 'O3F']:
        return 3
    elif result in ['O2', 'O2F']:
        return 2
    elif result == 'FT - MK':
        return 1
    return 0

def count_shots(result):
    return 1 if result in ['O2', 'O3', 'X2', 'X3', 'X3F', 'X2F', 'TO'] else 0

def count_turnovers(result):
    return 1 if result == 'TO' else 0

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

def count_our_offensive_rebounds(result):
    return 1 if result == 'GT Off Reb' else 0

def count_opponent_offensive_rebounds(result):
    return 1 if result == 'Opp Off Reb' else 0

def load_and_process_data(folder_path):
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
    combined_df = pd.concat(dataframes, ignore_index=True)
    
    # Aggregate the summed stats for each lineup
    lineup_stats = combined_df.groupby('ON COURT').agg({
        'Points': 'sum',
        'Shots': 'sum',
        'Turnovers': 'sum',
        'FG Made': 'sum',
        'FG Attempted': 'sum',
        '3P Made': 'sum',
        '3P Attempted': 'sum',
        'FT Made': 'sum',
        'FT Attempted': 'sum',
        'Our Off Reb': 'sum',
        'Opp Off Reb': 'sum'
    }).reset_index()

    # Calculate percentages and points per shot
    lineup_stats['FG%'] = (lineup_stats['FG Made'] / lineup_stats['FG Attempted']).round(3) * 100
    lineup_stats['3P%'] = (lineup_stats['3P Made'] / lineup_stats['3P Attempted']).round(3) * 100
    lineup_stats['FT%'] = (lineup_stats['FT Made'] / lineup_stats['FT Attempted']).round(3) * 100
    lineup_stats['Points per Shot'] = (lineup_stats['Points'] / lineup_stats['Shots']).round(3)
    lineup_stats['Turnover Percentage'] = (lineup_stats['Turnovers'] / lineup_stats['Shots']).round(3) * 100  # Assuming shots represent possessions
    lineup_stats['Our Off Reb %'] = (lineup_stats['Our Off Reb'] / lineup_stats['Shots']).round(3) * 100
    lineup_stats['Opp Off Reb %'] = (lineup_stats['Opp Off Reb'] / lineup_stats['Shots']).round(3) * 100

    # Merge the aggregated stats with the frequency table
    frequency_table = combined_df['ON COURT'].value_counts().reset_index()
    frequency_table.columns = ['Lineup', 'Frequency']
    final_table = frequency_table.merge(lineup_stats, left_on='Lineup', right_on='ON COURT')

    # Select and order columns for the final table
    final_table = final_table[['Lineup', 'Frequency', 'Points', 'Points per Shot', 'Turnovers', 'Turnover Percentage',
                               'FG Made', 'FG Attempted', 'FG%', '3P Made', '3P Attempted', '3P%', 'FT Made', 'FT Attempted', 'FT%']]
    return final_table

# Streamlit app starts here
st.title('Georgia Tech Lineup Analysis')

# User input for folder path
folder_path = st.text_input('Enter the folder path for CSV files:', 'game-csv-2023')

if st.button('Analyze Data'):
    if os.path.exists(folder_path):
        # Load, process data, and display the table
        try:
            final_table = load_and_process_data(folder_path)
            st.write(final_table)
        except Exception as e:
            st.error(f'An error occurred: {e}')
    else:
        st.error('Folder does not exist. Please enter a valid folder path.')
