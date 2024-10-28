import pandas as pd
import os
import glob
import pytz

def getTrainingAverages():

    folder_path = 'BoltsSportsScienceReports/Detailed_Training_Sessions'

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    dataframes = []
    # Filter filenames that contain both player_name and opp_name
    for f in csv_files:
        file_path = os.path.join(folder_path, f)
        
        # Read the CSV file into a DataFrame
        pd_df = pd.read_csv(file_path)
        
        pd_df['athlete_name'] = pd_df['athlete_name'].str.lower()
        
        # Append the DataFrame to the list
        dataframes.append(pd_df)
        
    playerdata_df = pd.concat(dataframes, ignore_index=True)

    # Convert start_time from string to datetime in UTC
    playerdata_df['start_time'] = pd.to_datetime(playerdata_df['start_time'])

    # Set the timezone to UTC, then convert to EST
    playerdata_df['start_time'] = playerdata_df['start_time'].dt.tz_convert('America/New_York')

    playerdata_df['Day of Week'] = pd.to_datetime(playerdata_df['start_time']).dt.day_name()

    u19 = playerdata_df.loc[playerdata_df['bolts team'] == 'Boston Bolts MLS Next U19']

    playerdata_df.drop(columns={'session_type'}, inplace=True)


    def rearrange_team_name(team_name):
        # Define age groups and leagues
        age_groups = ['U15', 'U16', 'U17', 'U19', 'U13', 'U14']
        leagues = ['MLS Next', 'NAL Boston', 'NAL South Shore']
        
        # Find age group in the team name
        for age in age_groups:
            if age in team_name:
                # Find the league part
                league_part = next((league for league in leagues if league in team_name), '')
                if league_part == 'NAL Boston':
                    league_part = 'NALB'
                
                # Extract the rest of the team name
                rest_of_name = team_name.replace(age, '').replace('NAL Boston', '').replace(league_part, '').strip()
                
                
                # Construct the new team name
                return f"{rest_of_name} {age} {league_part}"
        
        # Return the original team name if no age group is found
        return team_name

    # Apply the function to the 'team_name' column
    playerdata_df['bolts team'] = playerdata_df['bolts team'].apply(rearrange_team_name)

    # Getting rid of outliers
    playerdata_df = playerdata_df[playerdata_df['total_distance_m'] > 2000]

    days_of_week = ['Tuesday', 'Wednesday', 'Thursday']

    playerdata_df = playerdata_df.loc[playerdata_df['Day of Week'].isin(days_of_week)]

    weekly_grouped = playerdata_df.groupby([pd.Grouper(key='start_time', freq='W'), 'athlete_name', 'bolts team']).agg({
        'total_distance_m': 'sum',
        'total_high_intensity_distance_m': 'sum',
        'start_time': 'count'  # This will count the number of data points
    }).rename(columns={'start_time': 'data_point_count'}).reset_index()

    weekly_grouped = weekly_grouped.loc[weekly_grouped['data_point_count'] == 3]

    return weekly_grouped
