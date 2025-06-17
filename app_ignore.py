import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go

df = pd.read_csv('comrades_2025_results.csv')




df['Pos'] = df['Pos'].astype('Int32')
df['Cat Pos'] = df['Cat Pos'].astype('Int32')
df['Gen Pos'] = df['Gen Pos'].astype('Int32')

# create a new column for the percentile of the participant's position
# df['Percentile'] = df['Pos'].rank(pct=True, ascending=True)

# creat a new column indicating the fraction of participants that the participant beat
df['Percentile Pos'] = df['Pos'] / len(df)

# Group by 'Category' and calculate category size, then merge back to get category counts
category_sizes = df.groupby('Category').size().reset_index(name='category_size')
df = df.merge(category_sizes, on='Category', how='left')

# Calculate percentile within category
df['Percentile Cat Pos'] = df['Cat Pos'] / df['category_size']

df['Fraction Beaten'] = 1 - ((df['Pos'] - 1) / (len(df) - 1))

# create a new column for the percentile of the participant's category position
# df['Cat Percentile'] = df['Cat Pos'].rank(pct=True, ascending=False)

# convert the values of DNF, Not started, UOF, Started in the time column to their own boolean columns
df['DNF'] = df['Time'].str.contains('DNF')
df['Not started'] = df['Time'].str.contains('Not started')
df['UOF'] = df['Time'].str.contains('UOF')
df['Started'] = df['Time'].str.contains('Started') 
df['DNS'] = df['Time'].str.contains('DNS') 

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

def format_timedelta_without_days(td):
    if pd.isna(td):
        return ""
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"

# Apply the formatting function to the 'Time' column
df['TimeFormatted'] = df['Time'].apply(format_timedelta_without_days)


st.title('Comrades 2025 Results Analysis')

# add a selectbox to choose the participant
participant = st.selectbox('Select a participant:', df['Name'].unique())



# display the participant's details
participant_details = df[df['Name'] == participant].iloc[0]
# st.write(f"**Country:** {participant_details['Country']}")
# st.write(f"**Position:** {participant_details['Pos']}")
# st.write(f"**Category Position:** {participant_details['Cat Pos']}")

# display a country flag for the participant's country
country = participant_details['Flag']
try:
    flag_url = f"https://flagcdn.com/w80/{country.lower()}.png"
    st.markdown(
        f"""
        <div style="text-align: center; margin: 20px">
            <img src="{flag_url}" alt="{country} flag" style="width: 64px; height: 48px;">
        </div>
        """,
        unsafe_allow_html=True
    )
except: 
    pass # If the flag URL is not valid, we can skip displaying it

def display_gauge_chart(col):
    # Create a gauge chart showing the participant's percentile
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = participant_details[col] * 100,
        number = {'valueformat': '.2f', 'suffix': '%'},  # Added suffix for percentage symbol
        title = {'text': "Overall Performance Percentile"},
        
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33.33], 'color': "green"},
                {'range': [33.33, 66.67], 'color': "yellow"},
                {'range': [66.67, 100], 'color': "red"}
            ]
        }
    ))

    st.plotly_chart(fig_gauge, use_container_width=True, key=col)


col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f"""
        <div style="text-align: center; border: 2px solid #ccc; border-radius: 10px; padding: 20px; margin: 10px">
            <h3>Time</h3>
            <h1 style="font-size: 40px">{participant_details['TimeFormatted']}</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    display_gauge_chart('Fraction of Cut Off')
    
with col2:
    st.markdown(
        f"""
        <div style="text-align: center; border: 2px solid #ccc; border-radius: 10px; padding: 20px; margin: 10px">
            <h3>Position</h3>
            <h1 style="font-size: 40px">{participant_details['Pos']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    display_gauge_chart('Percentile Pos')

with col3:
    st.markdown(
        f"""
        <div style="text-align: center; border: 2px solid #ccc; border-radius: 10px; padding: 20px; margin: 10px">
            <h3>Category Position</h3>
            <h1 style="font-size: 40px">{participant_details['Cat Pos']}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    display_gauge_chart('Percentile Cat Pos')


# Create scatter plot with Plotly Express
fig = px.strip(df, 
               x='Time (hours)',
               title='Distribution of Finish Times at the 2025 Comrades Marathon',
               template='simple_white'
               )
fig.update_layout(title_font_size=24)

fig.update_traces(
    jitter=1,
    marker=dict(
        size=3,
        opacity=0.3
    ),
    text=df['Name'],
    hovertemplate='<b>%{text}</b><br>Time: %{x:.2f} hours<extra></extra>'
)


fig.add_vline(x=6, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Wally Hayward Cut-Off ', annotation_position='bottom left')
fig.add_vline(x=7, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Isavel Roche-Kelly Cut-Off ', annotation_position='bottom left')
fig.add_vline(x=7.5, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Silver Cut-Off ', annotation_position='bottom left')
fig.add_vline(x=9, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Bill Rowan Cut-Off ', annotation_position='bottom left')
fig.add_vline(x=10, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Robert Mtshali Cut-Off ', annotation_position='bottom left')
fig.add_vline(x=11, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Bronze Cut-Off ', annotation_position='bottom left')
fig.add_vline(x=12, line=dict(color='black', width=0.6, dash='dash'),
              annotation_text='Vic Clapham Cut-Off ', annotation_position='bottom left')

# Add vertical lines for hour markers
# for i in range(5, 13):
#     fig.add_vline(x=i, line=dict(color='red', width=1, dash='dash'),
#                   annotation_text=f'{i} hours', annotation_position='top left')
    
# add vertical line for participant_details finish time
if participant_details['Time (hours)'] is not pd.NaT:
    fig.add_vline(x=participant_details['Time (hours)'], 
                  line=dict(color='green', width=2, dash='solid'),
                  annotation_text=f'{participant_details["Name"].upper()}', 
                  annotation_position='top')
    

# Update layout
fig.update_layout(
    showlegend=False,
    xaxis_title="Time (hours)",
    yaxis_showticklabels=False,
    height=600
)

st.plotly_chart(fig, use_container_width=True)



# # Create a gauge chart showing the participant's percentile
# fig_gauge = go.Figure(go.Indicator(
#     mode = "gauge+number",
#     value = participant_details['Percentile'] * 100,
#     number = {'valueformat': '.2f', 'suffix': '%'},  # Added suffix for percentage symbol
#     title = {'text': "Overall Performance Percentile"},
#     gauge = {
#         'axis': {'range': [0, 100]},
#         'bar': {'color': "darkblue"},
#         'steps': [
#             {'range': [0, 40], 'color': "green"},
#             {'range': [40, 70], 'color': "yellow"},
#             {'range': [70, 100], 'color': "red"}
#         ]
#     }
# ))

# st.plotly_chart(fig_gauge, use_container_width=True)



# add a donut chart showing the distribution of participants by country
# fig_pie = px.pie(df, 
#                  names='Gender', 
#                  color_discrete_sequence=px.colors.qualitative.Pastel,
#                  hole=0.4)
# st.plotly_chart(fig_pie, use_container_width=True)






# MAKE the marker for participant with the name Darren CONYNGHAM triple in size and change the color to red
# fig.for_each_trace(lambda t: t.update(marker=dict(size=50, color='red', alpha=1))
#                    if t.name == 'Darren CONYNGHAM' else ())

# Display in Streamlit

#display the plotly express pie chart in streamlit app
# st.plotly_chart(px.pie(df,
#         values='Country',
#         title='Countries with Participants in Comrades 2025',
#         color_discrete_sequence=px.colors.qualitative.Pastel),
#         use_container_width=True )

# sns.stripplot(data=df, x='Time (seconds)', orient='h', palette='viridis', jitter=0.35, alpha=0.3)
# for i in range(5, 13):
#     plt.axvline(x=i * 60 * 60, color='red', linestyle='--', alpha=0.3, label=f'{i} hours')