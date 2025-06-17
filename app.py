import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

st.title('Comrades 2025 Results Analysis')
st.markdown('This app allows you to explore the results of the Comrades Marathon 2025. ' \
'You can view the distribution of finish times, the top countries by number of participants, and the distribution of participants by age category. ' \
'You can also select a participant to view their details.')

df = pd.read_csv('comrades_2025_results.csv')

df['Pos'] = df['Pos'].astype('Int32')
df['Cat Pos'] = df['Cat Pos'].astype('Int32')
df['Gen Pos'] = df['Gen Pos'].astype('Int32')

# convert the values of DNF, Not started, UOF, Started in the time column to their own boolean columns
df['DNF'] = df['Time'].str.contains('DNF')
df['Not started'] = df['Time'].str.contains('Not started')
df['UOF'] = df['Time'].str.contains('UOF')
df['Started'] = df['Time'].str.contains('Started') 
df['DNS'] = df['Time'].str.contains('DNS') 

# create a single column called 'Status' that contains the status of the participant
df['Status'] = np.select(
    [df['DNF'], df['Not started'], df['UOF'], df['Started'], df['DNS']],
    ['Did Not Finish', 'Not started', 'Unofficial Finisher', 'Started', 'Did Not Start'],
    default='Finished'
)

# create a horizontal bar chart showing the distribution of participants by status
fig_bar_status = px.bar(df['Status'].value_counts().sort_values(ascending=True).reset_index(),
                        x='count',
                        y='Status',
                        title='Number of Participants by Finishing Status',
                        color_discrete_sequence=['darkred'],
                        orientation='h')
fig_bar_status.update_layout(
    title_font_size=24,
    font=dict(size=14),
    xaxis_title="Number of Participants",
    yaxis_title="Status",
    xaxis=dict(
        tickfont=dict(size=16)
    ),
    yaxis=dict(
        tickfont=dict(size=16)
    )
)
fig_bar_status.update_traces(
    textposition='inside',
    text=df['Status'].value_counts().sort_values(ascending=True),
    texttemplate='%{text:,}'
)
st.plotly_chart(fig_bar_status, use_container_width=True)



# create a horizontal bar chart showing the top 10 countries by number of participants
top_10_countries = df['Country'].value_counts().nlargest(5).sort_values(ascending=True)
fig_bar_countries = px.bar(top_10_countries.reset_index(),
                        x='count',
                        y='Country',
                        title='Top 5 Countries by Number of Participants',
                        color_discrete_sequence=['darkgreen'],
                        orientation='h')
fig_bar_countries.update_layout(
    title_font_size=24,
    font=dict(size=14),
    xaxis_title="Number of Participants",
    yaxis_title="Country",
    xaxis=dict(
        tickfont=dict(size=16)
    ),
    yaxis=dict(
        tickfont=dict(size=16)
    )
)
fig_bar_countries.update_traces(
    textposition='inside',
    text=top_10_countries,
    texttemplate='%{text:,}'
)
st.plotly_chart(fig_bar_countries, use_container_width=True)


# create a horizontal bar chart showing the distribution of participants by Category
cat_dist = df['Category'].value_counts().sort_values(ascending=True)
fig_bar_cat = px.bar(cat_dist.reset_index(),
                        x='count',
                        y='Category',
                        title='Number of Participants by Age Category',
                        color_discrete_sequence=['darkorange'],
                        orientation='h')
fig_bar_cat.update_layout(
    title_font_size=24,
    font=dict(size=14),
    xaxis_title="Number of Participants",
    yaxis_title="Category",
    xaxis=dict(
        tickfont=dict(size=16)
    ),
    yaxis=dict(
        tickfont=dict(size=16)
    )
)
fig_bar_cat.update_traces(
    textposition='inside',
    text=cat_dist,
    texttemplate='%{text:,}'
)
st.plotly_chart(fig_bar_cat, use_container_width=True)




# remove the DNF, Not started, UOF, and Started values from the Time column
df['Time'] = df['Time'].str.replace('DNF', '', regex=False)
df['Time'] = df['Time'].str.replace('Not started', '', regex=False)
df['Time'] = df['Time'].str.replace('UOF', '', regex=False)
df['Time'] = df['Time'].str.replace('Started', '', regex=False)
df['Time'] = df['Time'].str.replace('DNS', '', regex=False)
# convert the Time column to a timedelta
df['Time'] = pd.to_timedelta(df['Time'], errors='coerce')


# remove the DNF, Not started, UOF, and Started values from the Time column
df['Net Time'] = df['Net Time'].str.replace('DNF', '', regex=False)
df['Net Time'] = df['Net Time'].str.replace('Not started', '', regex=False)
df['Net Time'] = df['Net Time'].str.replace('UOF', '', regex=False)
df['Net Time'] = df['Net Time'].str.replace('Started', '', regex=False)
df['Net Time'] = df['Net Time'].str.replace('DNS', '', regex=False)
# convert the Time column to a timedelta
df['Net Time'] = pd.to_timedelta(df['Net Time'], errors='coerce')


#convert the 'Time' column to seconds for easier calculations
df['Time (seconds)'] = df['Time'].dt.total_seconds()
df['Fraction of Cut Off'] = df['Time (seconds)'] / (60 * 60 * 12)
#convert the 'Time' column to minutes
df['Time (minutes)'] = df['Time (seconds)'] / 60
#convert the 'Time' column to hours
df['Time (hours)'] = df['Time (minutes)'] / 60

# split the 'Wave' column into two columns on the " - " delimiter
df[['Batch Latter', 'Wave Number']] = df['Wave'].str.split(' - ', expand=True)


def format_timedelta_without_days(td):
    if pd.isna(td):
        return ""
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"

# Apply the formatting function to the 'Time' column
df['TimeFormatted'] = df['Time'].apply(format_timedelta_without_days)



# Create strip plot with Plotly Express
fig2 = px.strip(df.sort_values(by='Wave'), 
               y='Time (hours)',
               title='Distribution of Finish Times at Comrades Marathon 2025 by Wave',
               template='simple_white',
               color='Wave',  # Color by Wave Number
               color_discrete_sequence=px.colors.qualitative.Set1  # Changed to bolder Set1 colors
               )

fig2.update_layout(
    title_font_size=24,
    yaxis={'autorange': 'reversed',
           'ticksuffix': ' hours'},  # Add 'hours' suffix to y-axis labels
    showlegend=True,
    xaxis_title="Time (hours)", 
    xaxis_showticklabels=True,
    yaxis_showticklabels=True,
    height=900,
    font=dict(size=14),  # Increase general font size
    legend=dict(
        font=dict(size=20),  # Increased legend font size
        itemsizing='constant',  # Make legend items consistent size
        itemwidth=30  # Increase width of legend items
    )
)

fig2.update_traces(
    jitter=1,
    marker=dict(
        size=3,
        opacity=0.3
    )
)

fig2.add_hline(y=6, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Wally Hayward Cut-Off ', annotation_position='bottom right')
fig2.add_hline(y=7, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Isavel Roche-Kelly Cut-Off ', annotation_position='bottom right')
fig2.add_hline(y=7.5, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Silver Cut-Off ', annotation_position='bottom right')
fig2.add_hline(y=9, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Bill Rowan Cut-Off ', annotation_position='bottom right')
fig2.add_hline(y=10, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Robert Mtshali Cut-Off ', annotation_position='bottom right')
fig2.add_hline(y=11, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Bronze Cut-Off ', annotation_position='bottom right')
fig2.add_hline(y=12, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Vic Clapham Cut-Off ', annotation_position='bottom right')

fig2.update_traces(
    jitter=1,
    marker=dict(
        size=3,
        opacity=0.3
    )
)

st.plotly_chart(fig2, use_container_width=True)


# add a selectbox to choose the participant
participant = st.selectbox('Select a participant:', list(df['Name'].unique()))

# display the participant's details
participant_details = df[df['Name'] == participant].iloc[0]

# Create strip plot with Plotly Express
fig = px.strip(df, 
               y='Time (hours)',
               title='Overall Distribution of Finish Times at Comrades Marathon 2025',
               template='simple_white'
               )

fig.update_layout(
    title_font_size=24,
    yaxis={'autorange': 'reversed',
           'ticksuffix': ' hours'},  # Add 'hours' suffix to y-axis labels
    showlegend=False,
    xaxis_title="Time (hours)",
    yaxis_showticklabels=True,
    height=900,
    font=dict(size=14),  # Increase general font size
)

fig.update_traces(
    jitter=1,
    marker=dict(
        size=3,
        opacity=0.3
    ),
    text=df['Name'],
    hovertemplate='<b>%{text}</b><br>Time: %{y:.2f} hours<extra></extra>'
)


fig.add_hline(y=6, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Wally Hayward Cut-Off ', annotation_position='bottom right')
fig.add_hline(y=7, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Isavel Roche-Kelly Cut-Off ', annotation_position='bottom right')
fig.add_hline(y=7.5, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Silver Cut-Off ', annotation_position='bottom right')
fig.add_hline(y=9, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Bill Rowan Cut-Off ', annotation_position='bottom right')
fig.add_hline(y=10, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Robert Mtshali Cut-Off ', annotation_position='bottom right')
fig.add_hline(y=11, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Bronze Cut-Off ', annotation_position='bottom right')
fig.add_hline(y=12, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Vic Clapham Cut-Off ', annotation_position='bottom right')


if participant_details['Time (hours)'] is not pd.NaT:
    fig.add_hline(y=participant_details['Time (hours)'], 
                  line=dict(color='green', width=1, dash='solid'),
                  annotation_text=f'{participant_details["Name"].upper()}', 
                  annotation_position='top left')


st.plotly_chart(fig, use_container_width=True)

# Create a footer saying "Created by [Your Name]"
st.markdown("---")
st.markdown("Created by Darren Conyngham")