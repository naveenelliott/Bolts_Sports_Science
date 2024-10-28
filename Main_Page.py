import pandas as pd
import streamlit as st
import plotly.express as px
from GetPlayerTrainingAverages import getTrainingAverages

st.set_page_config(page_title='Bolts Training Reports', page_icon = 'Training.png')

training_averages = getTrainingAverages()

training_averages[['total_distance_m', 'total_high_intensity_distance_m']] = training_averages[['total_distance_m', 'total_high_intensity_distance_m']].astype(float)

training_averages = training_averages.groupby(['athlete_name', 'bolts team']).agg({
    'total_distance_m': 'mean',
    'total_high_intensity_distance_m': 'mean'
}).reset_index()

teams = sorted(list(training_averages['bolts team'].unique()))


selected_team = st.session_state.get('selected_team', teams[0])
if selected_team not in teams:
    selected_team = teams[0]  # Default to the first date if not found

selected_team = st.selectbox('Choose a Bolts Team:', teams, index=teams.index(selected_team))

training_averages = training_averages.loc[training_averages['bolts team'] == selected_team].reset_index(drop=True)
del training_averages['bolts team']
training_averages['total_distance_m'] = round(training_averages['total_distance_m'], 2)
training_averages['total_high_intensity_distance_m'] = round(training_averages['total_high_intensity_distance_m'], 2)
training_averages.rename(columns={'total_distance_m': 'Total Dist', 
                                  'total_high_intensity_distance_m': 'HID'}, inplace=True)
training_averages.sort_values('Total Dist', ascending=False, inplace=True)
training_averages.reset_index(drop=True, inplace=True)

col1, col2 = st.columns(2)

with col1:
    st.write(training_averages)

with col2:
    fig = px.scatter(
        training_averages,
        x='Total Dist',
        y='HID',
        hover_name='athlete_name',
        title='Training Averages by Athlete', 
    )

    fig.update_traces(marker=dict(color='lightblue', size=10))

    # Remove the grid lines
    fig.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)
