import streamlit as st
import pandas as pd
import os
import re

# functions for specific calculations
def count_shots(result):
    return 1 if result in ['O2', 'O3', 'X2', 'X3', 'X3F', 'X2F', 'TO'] else 0

def style_plus_minus(val):
    """
    Returns the style configuration for the '+/-' column based on the value.
    """
    if val > 0:
        return {'backgroundColor': 'green', 'color': 'white'}
    elif val < 0:
        return {'backgroundColor': 'red', 'color': 'white'}
    else:
        return {}

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


def count_rebounds(df, column, term):
    return df[column].apply(lambda x: x.split(',').count(term) if isinstance(x, str) else 0)


def process_stats(df, offense_or_defense):
    filtered_df = df[df['Row'] == offense_or_defense]

    if offense_or_defense == 'OFFENSE':
        rebound_term = 'GT Off Reb'
        rebound_column_name = 'GT Offensive Rebounds'
        filtered_df[rebound_column_name] = count_rebounds(filtered_df, 'OFFENSE', rebound_term)
    else:
        rebound_term = 'Opp Off Reb'
        rebound_column_name = 'Opponent Offensive Rebounds'
        filtered_df[rebound_column_name] = count_rebounds(filtered_df, 'DEFENSE', rebound_term)

    filtered_df['Points'] = filtered_df['Result'].apply(calculate_points)
    filtered_df['Shots'] = filtered_df['Result'].apply(count_shots)
    filtered_df['Turnovers'] = filtered_df['Result'].apply(count_turnovers)
    filtered_df['FG Made'] = filtered_df['Result'].apply(count_field_goals_made)
    filtered_df['FG Attempted'] = filtered_df['Result'].apply(count_field_goals_attempted)
    filtered_df['3P Made'] = filtered_df['Result'].apply(count_three_point_made)
    filtered_df['3P Attempted'] = filtered_df['Result'].apply(count_three_point_attempted)
    filtered_df['FT Made'] = filtered_df['Result'].apply(count_free_throws_made)
    filtered_df['FT Attempted'] = filtered_df['Result'].apply(count_free_throws_attempted)

    # adjust possessions calculation by subtracting rebounds
    filtered_df['Possessions'] = filtered_df['Shots'] + filtered_df['Turnovers'] - filtered_df[rebound_column_name]

    # aggregation functions
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
        'Possessions': 'sum',
        rebound_column_name: 'sum'
    }

    stats = filtered_df.groupby('ON COURT').agg(agg_functions).reset_index()

    stats['PPP'] = (stats['Points'] / stats['Shots']).round(3)
    stats['FG%'] = (stats['FG Made'] / stats['FG Attempted']).round(3) * 100
    stats['3P%'] = (stats['3P Made'] / stats['3P Attempted']).round(3) * 100
    stats['FT%'] = (stats['FT Made'] / stats['FT Attempted']).round(3) * 100
    stats['Turnover Percentage'] = (stats['Turnovers'] / stats['Possessions']).round(3) * 100

    stats['Offensive Rebound %'] = ((stats[rebound_column_name] / stats['Possessions']).round(3)) * 100


    cols = ['ON COURT', 'Possessions', 'Points', 'PPP', 
            'FG Made', 'FG Attempted', 'FG%', '3P Made', '3P Attempted', 
            '3P%', rebound_column_name, 'Offensive Rebound %', 'Turnovers', 'Turnover Percentage', 'FT Made', 
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

        half_court_offense = 'HALF COURT OFFENSE' if 'HALF COURT OFFENSE' in df.columns else ''
        half_court_actions = 'HALF COURT ACTIONS' if 'HALF COURT ACTIONS' in df.columns else ''

        if half_court_offense and half_court_actions:
            df['Half Court Combined'] = df[half_court_offense].fillna('') + ',' + df[half_court_actions].fillna('')
        elif half_court_offense:
            df['Half Court Combined'] = df[half_court_offense]
        elif half_court_actions:
            df['Half Court Combined'] = df[half_court_actions]
        else:
            df['Half Court Combined'] = ''

        df['Half Court Combined'] = df['Half Court Combined'].str.strip(',')

        dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df


# streamlit app layout
st.markdown("Created by: Ankith Kodali (more commonly known as AK)")

# logo
col1, col2 = st.columns([1, 4])

with col1:
    st.image('gtlogo.svg', width=120)

with col2:
    st.title('Lineup Analysis')

# listing of files in 'game-csv-2023' folder
try:
    files_with_extension = [f for f in os.listdir('game-csv-2023') if f.endswith('.csv')]
    files = [f[:-4] for f in files_with_extension]  # Remove the '.csv' from each filename
    selected_files_with_extension = st.multiselect('Select game for analysis:', files)
    selected_files = [f + '.csv' for f in selected_files_with_extension]  # Add back the '.csv' for processing
except Exception as e:
    st.error(f'Error accessing folder: {e}')

# load data button
if st.button('Load Data'):
    if selected_files:
        try:
            combined_df = load_and_process_data(selected_files)
            st.session_state['combined_df'] = combined_df
            st.session_state['data_loaded'] = True
            st.success('Data loaded successfully')
        except Exception as e:
            st.error(f'An error occurred: {e}')
    else:
        st.error('No files selected. Please select files for analysis.')

# filtering options
if 'data_loaded' in st.session_state and st.session_state['data_loaded']:
    # filter for half court actions
    combined_actions = st.session_state['combined_df']['Half Court Combined'].dropna().unique()
    excluded_options = ['', 'NaN', 'ISO, DK/MVMT']
    combined_actions_options = [action for action in combined_actions if action not in excluded_options]
    selected_combined_actions = st.multiselect('Filter by Combined Half Court Actions:', combined_actions_options)

    # transition filter
    transition_options = st.session_state['combined_df']['TRANSITION'].dropna().unique()
    selected_transition = st.multiselect('Filter by Transition:', transition_options)

    # filter df
    filtered_df = st.session_state['combined_df']
    if selected_combined_actions:
        filtered_df = filtered_df[filtered_df['Half Court Combined'].isin(selected_combined_actions)]
    if selected_transition:
        filtered_df = filtered_df[filtered_df['TRANSITION'].isin(selected_transition)]

    # filtered data
    offensive_stats = process_stats(filtered_df, 'OFFENSE')
    defensive_stats = process_stats(filtered_df, 'DEFENSE')
    # +/- calc
    plus_minus_stats = offensive_stats[['ON COURT', 'Points']].merge(
        defensive_stats[['ON COURT', 'Points']], on='ON COURT', how='left', suffixes=('_Off', '_Def')
    )
    plus_minus_stats['+/-'] = plus_minus_stats['Points_Off'] - plus_minus_stats['Points_Def']

    # combine +/- with offense and defense stats
    offensive_stats = offensive_stats.merge(plus_minus_stats[['ON COURT', '+/-']], on='ON COURT')
    offensive_stats = offensive_stats[['ON COURT', '+/-'] + [col for col in offensive_stats.columns if col not in ['ON COURT', '+/-']]]
    defensive_stats = defensive_stats.merge(plus_minus_stats[['ON COURT', '+/-']], on='ON COURT')
    defensive_stats = defensive_stats[['ON COURT', '+/-'] + [col for col in defensive_stats.columns if col not in ['ON COURT', '+/-']]]

    # html for maybe color code
    offensive_html = offensive_stats.to_html(escape=False)
    defensive_html = defensive_stats.to_html(escape=False)


    # data based on user input
    min_poss = st.number_input('Enter minimum possessions for lineups to display:', min_value=1, value=5)
    view_mode = st.radio("View Mode", ('Offensive Stats', 'Defensive Stats'))
    if view_mode == 'Offensive Stats':
        filtered_data = offensive_stats[offensive_stats['Possessions'] >= min_poss]
        sorted_data = filtered_data.sort_values(by='Possessions', ascending=False)
        sorted_data.index = range(1, len(sorted_data) + 1)
        st.dataframe(sorted_data)

    elif view_mode == 'Defensive Stats':
        filtered_data = defensive_stats[defensive_stats['Possessions'] >= min_poss]
        sorted_data = filtered_data.sort_values(by='Possessions', ascending=False)
        sorted_data.index = range(1, len(sorted_data) + 1)
        st.dataframe(sorted_data)