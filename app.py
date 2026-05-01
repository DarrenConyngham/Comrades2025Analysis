import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.title('Comrades 2025 Results Analysis')
st.markdown('This app allows you to explore the results of the Comrades Marathon 2025. ' \
'You can view the distribution of finish times, the top countries by number of participants, and the distribution of participants by age category. ' \
'You can also select a participant to view their details.')


def format_timedelta_without_days(td):
    if pd.isna(td):
        return ""
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"


@st.cache_data
def load_results():
    df = pd.read_csv('comrades_2025_results.csv')

    df['Pos'] = df['Pos'].astype('Int32')
    df['Cat Pos'] = df['Cat Pos'].astype('Int32')
    df['Gen Pos'] = df['Gen Pos'].astype('Int32')
    df['Category Size'] = df.groupby('Category')['Category'].transform('size')
    df['Fraction Beaten'] = 1 - ((df['Pos'] - 1) / (len(df) - 1))
    category_denominator = df['Category Size'] - 1
    df['Category Fraction Beaten'] = np.where(
        category_denominator > 0,
        1 - ((df['Cat Pos'] - 1) / category_denominator),
        np.nan
    )

    status_masks = [
        df['Time'].str.contains('DNF', na=False),
        df['Time'].str.contains('Not started', na=False),
        df['Time'].str.contains('UOF', na=False),
        df['Time'].str.contains('Started', na=False),
        df['Time'].str.contains('DNS', na=False),
    ]
    df['Status'] = np.select(
        status_masks,
        ['Did Not Finish', 'Not started', 'Unofficial Finisher', 'Started', 'Did Not Start'],
        default='Finished'
    )

    # clean and convert Time columns
    status_strings = ['DNF', 'Not started', 'UOF', 'Started', 'DNS']
    for col in ['Time', 'Net Time']:
        for s in status_strings:
            df[col] = df[col].str.replace(s, '', regex=False)
        df[col] = pd.to_timedelta(df[col], errors='coerce')

    # convert Time to numeric units
    df['Time (seconds)'] = df['Time'].dt.total_seconds()
    df['Fraction of Cut Off'] = df['Time (seconds)'] / (60 * 60 * 12)
    df['Time (minutes)'] = df['Time (seconds)'] / 60
    df['Time (hours)'] = df['Time (minutes)'] / 60

    # split the 'Wave' column into two columns on the " - " delimiter
    df[['Batch Letter', 'Wave Number']] = df['Wave'].str.split(' - ', expand=True)

    df['TimeFormatted'] = df['Time'].apply(format_timedelta_without_days)

    return df


def make_bar_chart(data, y_col, title, color):
    fig = px.bar(data.reset_index(),
                 x='count',
                 y=y_col,
                 title=title,
                 color_discrete_sequence=[color],
                 orientation='h')
    fig.update_layout(
        title_font_size=24,
        font=dict(size=14),
        xaxis_title="Number of Participants",
        yaxis_title=y_col,
        xaxis=dict(tickfont=dict(size=16)),
        yaxis=dict(tickfont=dict(size=16)),
        margin=dict(r=80)
    )
    fig.update_traces(
        textposition='outside',
        text=data,
        texttemplate='%{text:,}',
        cliponaxis=False
    )
    return fig


def make_gauge_chart(value, title, color):
    gauge_value = value if pd.notna(value) and np.isfinite(value) else 0
    gauge_value = min(max(gauge_value, 0), 1)
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=gauge_value * 100,
        number={'valueformat': '.1f', 'suffix': '%'},
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 50], 'color': '#f2f2f2'},
                {'range': [50, 80], 'color': '#dbeafe'},
                {'range': [80, 100], 'color': '#dcfce7'},
            ],
        }
    ))
    fig.update_layout(height=260, margin=dict(t=55, b=20, l=20, r=20))
    return fig


def add_cutoff_lines(fig):
    cutoffs = [
        (6,   'Wally Hayward Cut-Off '),
        (7,   'Isavel Roche-Kelly Cut-Off '),
        (7.5, 'Silver Cut-Off '),
        (9,   'Bill Rowan Cut-Off '),
        (10,  'Robert Mtshali Cut-Off '),
        (11,  'Bronze Cut-Off '),
        (12,  'Vic Clapham Cut-Off '),
    ]
    for y, label in cutoffs:
        fig.add_hline(y=y, line=dict(color='black', width=0.6, dash='dash'),
                      annotation_text=label, annotation_position='bottom right')


def format_position(value):
    return "" if pd.isna(value) else f"{int(value):,}"


def show_participant_summary(participant_details):
    flag_code = participant_details['Flag']

    st.subheader(participant_details['Name'])
    header_cols = st.columns([1, 2, 2, 2])
    with header_cols[0]:
        if isinstance(flag_code, str) and len(flag_code) == 2 and flag_code != 'XX':
            st.image(f"https://flagcdn.com/w80/{flag_code.lower()}.png", width=64)
    with header_cols[1]:
        st.metric('Time', participant_details['TimeFormatted'] or participant_details['Status'])
    with header_cols[2]:
        st.metric('Overall Position', format_position(participant_details['Pos']))
    with header_cols[3]:
        st.metric('Category Position', format_position(participant_details['Cat Pos']))

    detail_cols = st.columns(3)
    with detail_cols[0]:
        st.metric('Country', participant_details['Country'])
    with detail_cols[1]:
        st.metric('Category', participant_details['Category'])
    with detail_cols[2]:
        st.metric('Race No', participant_details['Race No'])

    club = participant_details['Club'] if pd.notna(participant_details['Club']) else ''
    if club:
        st.metric('Club', club)

    gauge_cols = st.columns(2)
    with gauge_cols[0]:
        st.plotly_chart(
            make_gauge_chart(participant_details['Fraction Beaten'], 'Overall Field Beaten', '#2563eb'),
            use_container_width=True,
            key='overall_field_beaten',
        )
    with gauge_cols[1]:
        st.plotly_chart(
            make_gauge_chart(participant_details['Category Fraction Beaten'], 'Category Field Beaten', '#16a34a'),
            use_container_width=True,
            key='category_field_beaten',
        )


df = load_results()


participant_options = df.index.tolist()
participant_index = st.selectbox(
    'Select a participant:',
    participant_options,
    format_func=lambda i: f"{df.at[i, 'Name']} ({df.at[i, 'Race No']})",
)
participant_details = df.loc[participant_index]
show_participant_summary(participant_details)


# overall strip chart
fig_strip_overall = px.strip(df,
                              y='Time (hours)',
                              title='Overall Distribution of Finish Times at Comrades Marathon 2025',
                              hover_data=['Name', 'Country', 'Category', 'TimeFormatted'],
                              template='simple_white')

fig_strip_overall.update_layout(
    yaxis={'autorange': 'reversed', 'ticksuffix': ' hours'},
    showlegend=False,
    yaxis_showticklabels=True,
    height=700,
    font=dict(size=14),
)
fig_strip_overall.update_traces(jitter=1, marker=dict(size=3, opacity=0.3), text=df['Name'])
add_cutoff_lines(fig_strip_overall)

if pd.notna(participant_details['Time (hours)']):
    fig_strip_overall.add_hline(y=participant_details['Time (hours)'],
                                line=dict(color='orange', width=3, dash='solid'),
                                annotation_text=f'{participant_details["Name"].upper()}',
                                annotation_position='top left',
                                annotation=dict(font=dict(size=18)))

st.plotly_chart(fig_strip_overall, use_container_width=True)

st.markdown("---")

# distribution of participants by status
status_counts = df['Status'].value_counts().sort_values(ascending=True)
st.plotly_chart(make_bar_chart(status_counts, 'Status',
                               'Number of Participants by Finishing Status', 'darkred'),
                use_container_width=True)

# top 5 countries by number of participants
top_5_countries = df['Country'].value_counts().nlargest(5).sort_values(ascending=True)
st.plotly_chart(make_bar_chart(top_5_countries, 'Country',
                               'Top 5 Countries by Number of Participants', 'darkgreen'),
                use_container_width=True)

# distribution of participants by age category
cat_dist = df['Category'].value_counts().sort_values(ascending=True)
st.plotly_chart(make_bar_chart(cat_dist, 'Category',
                               'Number of Participants by Age Category', 'darkorange'),
                use_container_width=True)

# strip chart by wave/batch
fig_strip_wave = px.strip(df.sort_values(by='Wave'),
                           y='Time (hours)',
                           title='Distribution of Finish Times at Comrades Marathon 2025 by Group',
                           template='simple_white',
                           x='Batch Letter',
                           color='Wave Number',
                           hover_data=['Name', 'Country', 'Category', 'TimeFormatted'],
                           color_discrete_sequence=px.colors.qualitative.Set2)

fig_strip_wave.update_layout(
    title_font_size=24,
    yaxis={'autorange': 'reversed', 'ticksuffix': ' hours'},
    showlegend=True,
    xaxis_title="Batch",
    xaxis_showticklabels=True,
    yaxis_showticklabels=True,
    height=700,
    font=dict(size=14),
    legend=dict(
        font=dict(size=20),
        itemsizing='constant',
        itemwidth=30,
        y=1,
        x=0.5,
        xanchor="center",
        yanchor="top",
        orientation="h"
    )
)
fig_strip_wave.update_traces(jitter=1, marker=dict(size=3, opacity=0.3))
add_cutoff_lines(fig_strip_wave)
st.plotly_chart(fig_strip_wave, use_container_width=True)

st.markdown("---")
st.markdown("Created by Darren Conyngham")
