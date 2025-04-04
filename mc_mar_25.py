# =================================== IMPORTS ================================= #
import csv, sqlite3
import numpy as np 
import pandas as pd 
import seaborn as sns 
import matplotlib.pyplot as plt 
import plotly.figure_factory as ff
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
from folium.plugins import MousePosition
import plotly.express as px
import datetime
import folium
import os
import sys
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.development.base_component import Component
# 'data/~$bmhc_data_2024_cleaned.xlsx'
# print('System Version:', sys.version)
# -------------------------------------- DATA ------------------------------------------- #

current_dir = os.getcwd()
current_file = os.path.basename(__file__)
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = 'data/MarCom_Responses.xlsx'
file_path = os.path.join(script_dir, data_path)
data = pd.read_excel(file_path)
df = data.copy()

# Trim leading and trailing whitespaces from column names
df.columns = df.columns.str.strip()

# Trim whitespace from values in all columns
df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)


# Define a discrete color sequence
color_sequence = px.colors.qualitative.Plotly

# Filtered df where 'Date of Activity:' is in January
df['Date of Activity'] = pd.to_datetime(df['Date of Activity'], errors='coerce')
df = df[df['Date of Activity'].dt.month == 3]

# print(df)
# print(df[["Date of Activity", "Total travel time (minutes):"]])
# print('Total Marketing Events: ', len(df))
# print('Column Names: \n', df.columns.tolist())
# print('DF Shape:', df.shape)
# print('Dtypes: \n', df.dtypes)
# print('Info:', df.info())
# print("Amount of duplicate rows:", df.duplicated().sum())

# print('Current Directory:', current_dir)
# print('Script Directory:', script_dir)
# print('Path to data:',file_path)

# ================================= Columns ================================= #

# Column Names: 
#  Index([
#        'Timestamp',
#        'Which MarCom activity category are you submitting an entry for?',
#        'Person completing this form:', 
#        'Activity Duration (hours):',
#        'Purpose of the activity (please only list one):',
#        'Please select the type of product(s):',
#        'Please provide public information:', 
#        'Please explain event-oriented:',
#        'Date of Activity:', 
#        'Brief activity description:', 
#        'Total travel time (minutes):',
#        'Activity Status'],
#  dtype='object')

# print("Brief activity description: \n", df["Brief activity description:"].value_counts().to_string())

# =============================== Missing Values ============================ #

# missing = df.isnull().sum()
# print('Columns with missing values before fillna: \n', missing[missing > 0])

#  Please provide public information:    137
# Please explain event-oriented:        13

# ============================== Data Preprocessing ========================== #

# Check for duplicate columns
# duplicate_columns = df.columns[df.columns.duplicated()].tolist()
# print(f"Duplicate columns found: {duplicate_columns}")
# if duplicate_columns:
#     print(f"Duplicate columns found: {duplicate_columns}")

# Rename columns
df.rename(columns={"Which MarCom activity category are you submitting an entry for?": "MarCom Activity"}, inplace=True)
df.rename(columns={"Purpose of the activity (please only list one):": "Purpose"}, inplace=True)
df.rename(columns={"Please select the type of product(s):": "Product Type"}, inplace=True)
df.rename(columns={"Activity Duration (hours):": "Activity Duration"}, inplace=True)

# Fill Missing Values
df['Please provide public information:'] = df['Please provide public information:'].fillna('N/A')
df['Please explain event-oriented:'] = df['Please explain event-oriented:'].fillna('N/A')

# print(df.dtypes)

# ========================= Filtered DataFrames ========================== #

# -------------------------- MarCom Events --------------------------- #

marcom_events = len(df)
# print("Total Marcom events:", marcom_events)

# ---------------------------- MarCom Hours ---------------------------- #

# Remove the word 'hours' from the 'Activity duration:' column
df['Activity Duration'] = df['Activity Duration'].astype(str)  # Convert to string
df['Activity Duration'] = df['Activity Duration'].str.replace(' hours', '')
df['Activity Duration'] = df['Activity Duration'].str.replace(' hour', '')
df['Activity Duration'] = pd.to_numeric(df['Activity Duration'], errors='coerce')
# print('Column Names: \n', df.columns)

marcom_hours = df.groupby('Activity Duration').size().reset_index(name='Count')
marcom_hours = df['Activity Duration'].sum()
# print('Total Activity Duration:', sum_activity_duration, 'hours')

# ------------------------- Travel Time ------------------------------ #

df_mc_travel =df[["Date of Activity", "Total travel time (minutes):"]]
# print(df_mc_travel.head())

df["Total travel time (minutes):"] = df["Total travel time (minutes):"].fillna(0)
# print(df["Total travel time (minutes):"].value_counts())

# print(df["Total travel time (minutes):"].value_counts())

mc_travel = df["Total travel time (minutes):"].sum()
# mc_travel = df["Total travel time (minutes):"].sum()/60
# mc_travel = round(mc_travel)
# print("Total travel time:", mc_travel)

# --------------------------- MarCom Activity -------------------------- #

# Group by "Which MarCom activity category are you submitting an entry for?"
df_activities = df.groupby('MarCom Activity').size().reset_index(name='Count')
# print('Activities:\n', df_activities)

activity_bar=px.bar(
    df_activities,
    x='MarCom Activity',
    y='Count',
    color='MarCom Activity',
    text='Count',
).update_layout(
    height=460, 
    width=780,
    title=dict(
        text='MarCom',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-15,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            text=None,
            # text="Name",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False  # Hide x-tick labels
        # showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Name:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Person Pie Chart
activity_pie=px.pie(
    df_activities,
    names="MarCom Activity",
    values='Count'  # Specify the values parameter
).update_layout(
    height=460,
    width=780,
    title='MarCom Activity',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=0,
    textposition='auto',
    insidetextorientation='horizontal', 
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
)

# -------------------------- Person Completing Form ------------------------- #

# "Person completing this form:" dataframe:
df['Person submitting this form:'] = df['Person submitting this form:'].str.strip()
df['Person submitting this form:'] = df['Person submitting this form:'].replace('Felicia Chanlder', 'Felicia Chandler')
df_person = df.groupby('Person submitting this form:').size().reset_index(name='Count')
# print(df_person.value_counts())

person_bar=px.bar(
    df_person,
    x='Person submitting this form:',
    y='Count',
    color='Person submitting this form:',
    text='Count',
).update_layout(
    height=440, 
    width=780,
    title=dict(
        text='People Submitting Forms',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
        )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            text=None,
            # text="Name",
            font=dict(size=20),  # Font size for the title
        ),
        # showticklabels=False  # Hide x-tick labels
        showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        visible=False
        # visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Name:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Person Pie Chart
person_pie=px.pie(
    df_person,
    names="Person submitting this form:",
    values='Count'  # Specify the values parameter
).update_layout(
    title='Ratio of People Filling Out Forms',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=0,
    textposition='auto',
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
)

# --------------------- Activity Status --------------------- #

# "Activity Status" dataframe:
df_activity_status = df.groupby('Activity Status').size().reset_index(name='Count')

status_bar=px.bar(
    df_activity_status,
    x='Activity Status',
    y='Count',
    color='Activity Status',
    text='Count',
).update_layout(
    height=460, 
    width=780,
    title=dict(
        text='Activity Status',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=0,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Status",
            font=dict(size=20),  # Font size for the title
        ),
        # showticklabels=False  # Hide x-tick labels
        showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Status:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Person Pie Chart
status_pie=px.pie(
    df_activity_status,
    names="Activity Status",
    values='Count'  # Specify the values parameter
).update_layout(
    title='Activity Status',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=0,
    textposition='auto',
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
)

# --------------------------- Products Graphs -------------------------- #

data = [
    'AmeriCorps Responsibility', 
    'BMHC Board Meeting', 
    'BMHC PSA Videos Project',
    'Came up with social media verbiage for Student Videos', 
    'Flyer',
    'Gathered and sent Previous Meeting Minutes',
    'Intranet Updates',
    'Key Leader Huddle', 
    'Key Leaders Huddle', 
    'Key Leaders Meeting',
    'Man and Me schedule and post', 
    'MarCom Impact Report Meeting',
    'MarCom Playbook', 
    'Marcom Report',
    'Meeting - Communications',
    'Meeting - Impact Report', 
    'Meeting - Social Media', 
    'Meeting with Areebah',
    'Meeting with Director Pamela Parker',
    'Newsletter', 
    'Newsletter,',
    'Newsletter, Started Social Media and Newsletter Benchmarking',
    'Newsletter, edit Social Media and Newsletter Benchmarking',
    'No Product - Board Support', 
    'No Product - Branding Activity',
    'No Product - Co-branding in General', 
    'No product - Communications Support',
    'No product - Community Collaboration', 
    'No product - Event Support',
    'No product - Gathering Testimonials',
    'No product - Human Resources Training for Organizational Efficiency',
    'No product - Human Resources for Efficiency',
    'No product - Organizational Efficiency',
    'No product - Organizational Strategy',
    'Organization', 
    'Presentation', 
    'Presentation, Started Impact Report Presentation',
    'Press Release', 
    'Quarterly Team Meeting', 
    'Report',
    'Reviewed Student Videos',
    'Scheduled ACC Tax help with Areebah',
    'Scheduled Open Board Appointments and Man in Me Posts with Areebah',
    'Sustainability Binder',
    'Timesheet', 
    'Updated Marcom Data for December',
    'Updated verbiage for MLK Social Media post',
    'Video', 
    'Website Updates',
    'Worked on Video Inquiry and verbiage for ACC and UT',
    'Writing, Editing, Proofing', 
    'approved and scheduled UT PhARM Social Media Post',
    'created and updated Center of Excellence for Youth Mental Health logo',
    'meeting with Pamela', 
    'provided board minutes for audit',
    'sent Areebah a schedule posts list from the Newsletter',
    'updated - Board RFIs - January 2025', 
    'updated Board Due Outs file'
]

df['Product Type'] = (
    df['Product Type']
    .str.strip()
    .replace(
        {
            # No Product
            'No Product - Board Support': "No Product",
            'No Product - Branding Activity': "No Product",
            'No Product - Co-branding in General': "No Product",
            'No product - Communications Support': "No Product",
            'No product - Community Collaboration': "No Product",
            'No product - Event Support': "No Product",
            'No product - Gathering Testimonials': "No Product",
            'No product - Human Resources Training for Organizational Efficiency': "No Product",
            'No product - Human Resources for Efficiency': "No Product",
            'No product - Organizational Efficiency': "No Product",
            'No product - Organizational Strategy': "No Product",
            'No Product': "No Product",

            # Meetings
            'Meeting - Communications': "Meeting",
            'Meeting - Impact Report': "Meeting",
            'Meeting - Social Media': "Meeting",
            'Meeting with Areebah': "Meeting",
            'Meeting with Director Pamela Parker': "Meeting",
            'MarCom Impact Report Meeting': "Meeting",
            'meeting with Pamela': "Meeting",
            'BMHC Board Meeting': "Meeting",
            'Key Leader Huddle': "Meeting",
            'Key Leaders Huddle': "Meeting",
            'Key Leaders Meeting': "Meeting",
            'Scheduled ACC Tax help with Areebah': "Meeting",
            'Quarterly Team Meeting': "Meeting",
            'BMHC and Americorp Logo Requirements meeting': "Meeting",

            # Newsletter
            'Newsletter': "Newsletter",
            'Newsletter,': "Newsletter",
            'Newsletter, Started Social Media and Newsletter Benchmarking': "Newsletter",
            'Newsletter, edit Social Media and Newsletter Benchmarking': "Newsletter",

            # Presentations
            'Presentation': "Presentation",
            'Presentation, Started Impact Report Presentation': "Presentation",
            'Marcom Report': "Presentation",

            # Scheduling
            'Scheduled ACC Tax help with Areebah': "Scheduling",
            'Scheduled Open Board Appointments and Man in Me Posts with Areebah': "Scheduling",

            # Updates
            'updated - Board RFIs - January 2025': "Updates",
            'updated Board Due Outs file': "Updates",
            'Updated Marcom Data for December': "Updates",
            'Updated verbiage for MLK Social Media post': "Updates",
            'Website Updates': "Updates",
            'Update BMHC Service Webpage images': "Updates",
            'Updated ACC Student Video Post': "Updates",
            'Updated Felicia Chandler headshot in Photoshop for Website': "Updates",
            'Updated and Approve ACC Student Video Post': "Updates",
            'Updates': "Updates",
            'update and approved Organization chart': "Updates",
            'updated Red Card': "Updates",
            'updated and approved Red Card': "Updates",

            # Student-related activities
            'Came up with social media verbiage for Student Videos': "Student-related activity",
            'Reviewed Student Videos': "Student-related activity",
            'Worked on Video Inquiry and verbiage for ACC and UT': "Student-related activity",
            'Started SQL Certificates': "Student-related activity",

            # Social Media
            'approved and scheduled UT PhARM Social Media Post': "Social Media",
            'sent Areebah a schedule posts list from the Newsletter': "Social Media",
            'Man and Me schedule and post': "Social Media",
            'BMHC PSA Videos Project': "Social Media",
            'Social Media': "Social Media",

            # Editing/ Proofing/ Writing
            'Writing, Editing, Proofing': "Editing/ Proofing/ Writing",
            'created and updated Center of Excellence for Youth Mental Health logo': "Editing/ Proofing/ Writing",
            'BMHC Board Meeting': "Editing/ Proofing/ Writing",
            'Gathered and sent Previous Meeting Minutes': "Editing/ Proofing/ Writing",
            'Sustainability Binder': "Editing/ Proofing/ Writing",
            'MarCom Playbook': "Editing/ Proofing/ Writing",
            'provided board minutes for audit': "Editing/ Proofing/ Writing",
            'Editing/ Proofing/ Writing': "Editing/ Proofing/ Writing",

            # Other Product Types
            'AmeriCorp Logo': "Branding",
            'AmeriCorps Responsibility': "Branding",
            'Co-branding in general': "Branding",
            'Community Radio PSA/Promos': "Marketing",
            'Created Certificate Order Guide': "Administrative Task",
            'Flyer': "Marketing",
            'Impact Report': "Impact Report",
            'Move all files to BMHC Canva': "Administrative Task",
            'Organizational Efficiency': "Administrative Task",
            'Please Push - Board Member Garza': "Marketing",
            'Please Push - Community Health Worker position': "Marketing",
            'Press Release': "Marketing",
            'Report': "Report",
            'Timesheet': "Administrative Task",
            'created Red Card': "Design",
        }
    )
)


# Product Type dataframe:
df_product_type = df.groupby('Product Type').size().reset_index(name='Count')
# print(df_product_type["Product Type"].unique())

product_bar=px.bar(
    df_product_type,
    x='Product Type',
    y='Count',
    color='Product Type',
    text='Count',
).update_layout(
    height=990, 
    width=1700,
    title=dict(
        text='Product Type',
        x=0.5, 
        font=dict(
            size=25,
            family='Calibri',
            color='black',
            )
    ),
    font=dict(
        family='Calibri',
        size=18,
        color='black'
    ),
    xaxis=dict(
        tickangle=-15,  # Rotate x-axis labels for better readability
        tickfont=dict(size=18),  # Adjust font size for the tick labels
        title=dict(
            # text=None,
            text="Product",
            font=dict(size=20),  # Font size for the title
        ),
        showticklabels=False  # Hide x-tick labels
        # showticklabels=True  # Hide x-tick labels
    ),
    yaxis=dict(
        title=dict(
            text='Count',
            font=dict(size=20),  # Font size for the title
        ),
    ),
    legend=dict(
        # title='Support',
        title_text='',
        orientation="v",  # Vertical legend
        x=1.05,  # Position legend to the right
        y=1,  # Position legend at the top
        xanchor="left",  # Anchor legend to the left
        yanchor="top",  # Anchor legend to the top
        # visible=False
        visible=True
    ),
    hovermode='closest', # Display only one hover label per trace
    bargap=0.08,  # Reduce the space between bars
    bargroupgap=0,  # Reduce space between individual bars in groups
).update_traces(
    textposition='auto',
    hovertemplate='<b>Name:</b> %{label}<br><b>Count</b>: %{y}<extra></extra>'
)

# Person Pie Chart
product_pie=px.pie(
    df_product_type,
    names="Product Type",
    values='Count'  # Specify the values parameter
).update_layout(
    height=950,
    width=1700,
    title='Product Type Percentages',
    title_x=0.5,
    font=dict(
        family='Calibri',
        size=17,
        color='black'
    )
).update_traces(
    rotation=0,
    textposition='auto',
    # textinfo='none',
    textinfo='value+percent',
    hovertemplate='<b>%{label} Status</b>: %{value}<extra></extra>',
)

# # ========================== DataFrame Table ========================== #

# MarCom Table
marcom_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df[col] for col in df.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

marcom_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=400,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# Products Table
products_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df_product_type.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df_product_type[col] for col in df_product_type.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

products_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=850,
    width=700,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# Purpose dataframe:
df_purpose = df.groupby('Purpose').size().reset_index(name='Count')

# Purpose Table
purpose_table = go.Figure(data=[go.Table(
    # columnwidth=[50, 50, 50],  # Adjust the width of the columns
    header=dict(
        values=list(df_purpose.columns),
        fill_color='paleturquoise',
        align='center',
        height=30,  # Adjust the height of the header cells
        # line=dict(color='black', width=1),  # Add border to header cells
        font=dict(size=12)  # Adjust font size
    ),
    cells=dict(
        values=[df_purpose[col] for col in df_purpose.columns],
        fill_color='lavender',
        align='left',
        height=25,  # Adjust the height of the cells
        # line=dict(color='black', width=1),  # Add border to cells
        font=dict(size=12)  # Adjust font size
    )
)])

purpose_table.update_layout(
    margin=dict(l=50, r=50, t=30, b=40),  # Remove margins
    height=850,
    width=700,
    # width=1500,  # Set a smaller width to make columns thinner
    paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    plot_bgcolor='rgba(0,0,0,0)'  # Transparent plot area
)

# ============================== Dash Application ========================== #

app = dash.Dash(__name__)
server= app.server

app.layout = html.Div(
    children=[ 
    html.Div(
        className='divv', 
        children=[ 
        html.H1(
            'MarCom Report', 
            className='title'),
        html.H1(
            'March 2025', 
            className='title2'),
    html.Div(
        className='btn-box', 
        children=[
        html.A(
            'Repo',
            href='https://github.com/CxLos/MC_Mar_2025',
            className='btn'),
        ]),
    ]),    

# Data Table
# html.Div(
#     className='row0',
#     children=[
#         html.Div(
#             className='table',
#             children=[
#                 html.H1(
#                     className='table-title',
#                     children='Data Table'
#                 )
#             ]
#         ),
#         html.Div(
#             className='table2', 
#             children=[
#                 dcc.Graph(
#                     className='data',
#                     figure=marcom_table
#                 )
#             ]
#         )
#     ]
# ),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph11',
            children=[
            html.Div(
                className='high1',
                children=['MarCom Events:']
            ),
            html.Div(
                className='circle',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high2',
                            children=[marcom_events]
                    ),
                        ]
                    )
 
                ],
            ),
            ]
        ),
        html.Div(
            className='graph22',
            children=[
            html.Div(
                className='high3',
                children=['MarCom Hours:']
            ),
            html.Div(
                className='circle2',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high4',
                            children=[marcom_hours]
                    ),
                        ]
                    )
                ],
            ),
            ]
        ),
    ]
),

# ROW 1
html.Div(
    className='row1',
    children=[
        html.Div(
            className='graph11',
            children=[
            html.Div(
                className='high1',
                children=['Total Travel Time']
            ),
            html.Div(
                className='circle',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high6',
                            children=[mc_travel]
                    ),
                        ]
                    )
 
                ],
            ),
            ]
        ),
                html.Div(
            className='graph22',
            children=[
            html.Div(
                className='high3',
                children=['Blank']
            ),
            html.Div(
                className='circle2',
                children=[
                    html.Div(
                        className='hilite',
                        children=[
                            html.H1(
                            className='high4',
                            # children=[marcom_hours]
                    ),
                        ]
                    )
                ],
            ),
            ]
        ),
    ]
),

# ROW 3
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph1',
            children=[                
                dcc.Graph(
                    figure=activity_bar
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=activity_pie
                )
            ],
        ),
    ]
),

        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=product_bar
                        )
                    ]
                ),
            ]
        ),   
        
        html.Div(
            className='row3',
            children=[
                html.Div(
                    className='graph33',
                    children=[
                        dcc.Graph(
                            figure=product_pie
                        )
                    ]
                ),
            ]
        ),   

# ROW 2
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph3',
            children=[
                html.Div(
                    className='table',
                    children=[
                        html.H1(
                            className='table-title',
                            children='Products Table'
                        )
                    ]
                ),
                html.Div(
                    className='table2', 
                    children=[
                        dcc.Graph(
                            className='data',
                            figure=products_table
                        )
                    ]
                )
            ]
        ),
        html.Div(
            className='graph4',
            children=[                
              html.Div(
                    className='table',
                    children=[
                        html.H1(
                            className='table-title',
                            children='Purpose Table'
                        )
                    ]
                ),
                html.Div(
                    className='table2', 
                    children=[
                        dcc.Graph(
                            # className='data',
                            figure=purpose_table
                        )
                    ]
                )
   
            ]
        )
    ]
),

# ROW 4
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph1',
            children=[                
                dcc.Graph(
                    figure=person_bar
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=person_pie
                )
            ],
        ),
    ]
),

# ROW 4
html.Div(
    className='row2',
    children=[
        html.Div(
            className='graph1',
            children=[                
                dcc.Graph(
                    figure=status_bar
                )
            ]
        ),
        html.Div(
            className='graph2',
            children=[
                dcc.Graph(
                    figure=status_pie
                )
            ],
        ),
    ]
),

# html.Div(
#     className='row0',
#     children=[
#         html.Div(
#             className='table',
#             children=[
#                 html.H1(
#                     className='table-title',
#                     children='Purpose Table'
#                 )
#             ]
#         ),
#         html.Div(
#             className='table2', 
#             children=[
#                 dcc.Graph(
#                     className='data',
#                     figure=purpose_table
#                 )
#             ]
#         )
#     ]
# ),

# html.Div(
#     className='row0',
#     children=[
#         html.Div(
#             className='table',
#             children=[
#                 html.H1(
#                     className='table-title',
#                     children='Product Table'
#                 )
#             ]
#         ),
#         html.Div(
#             className='table2', 
#             children=[
#                 dcc.Graph(
#                     className='data',
#                     figure=products_table
#                 )
#             ]
#         )
#     ]
# ),
])

print(f"Serving Flask app '{current_file}'! 🚀")

if __name__ == '__main__':
    app.run_server(debug=True)
                #    False)
# =================================== Updated Database ================================= #

# updated_path = 'data/mc_feb_2025.xlsx'
# data_path = os.path.join(script_dir, updated_path)
# df.to_excel(data_path, index=False)
# print(f"DataFrame saved to {data_path}")

# updated_path1 = 'data/service_tracker_q4_2024_cleaned.csv'
# data_path1 = os.path.join(script_dir, updated_path1)
# df.to_csv(data_path1, index=False)
# print(f"DataFrame saved to {data_path1}")

# -------------------------------------------- KILL PORT ---------------------------------------------------

# netstat -ano | findstr :8050
# taskkill /PID 24772 /F
# npx kill-port 8050

# ---------------------------------------------- Host Application -------------------------------------------

# 1. pip freeze > requirements.txt
# 2. add this to procfile: 'web: gunicorn impact_11_2024:server'
# 3. heroku login
# 4. heroku create
# 5. git push heroku main

# Create venv 
# virtualenv venv 
# source venv/bin/activate # uses the virtualenv

# Update PIP Setup Tools:
# pip install --upgrade pip setuptools

# Install all dependencies in the requirements file:
# pip install -r requirements.txt

# Check dependency tree:
# pipdeptree
# pip show package-name

# Remove
# pypiwin32
# pywin32
# jupytercore

# ----------------------------------------------------

# Name must start with a letter, end with a letter or digit and can only contain lowercase letters, digits, and dashes.

# Heroku Setup:
# heroku login
# heroku create mc-impact-11-2024
# heroku git:remote -a mc-impact-11-2024
# git push heroku main

# Clear Heroku Cache:
# heroku plugins:install heroku-repo
# heroku repo:purge_cache -a mc-impact-11-2024

# Set buildpack for heroku
# heroku buildpacks:set heroku/python

# Heatmap Colorscale colors -----------------------------------------------------------------------------

#   ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
            #  'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
            #  'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
            #  'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
            #  'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
            #  'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
            #  'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
            #  'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
            #  'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
            #  'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
            #  'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
            #  'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
            #  'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
            #  'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
            #  'ylorrd'].

# rm -rf ~$bmhc_data_2024_cleaned.xlsx
# rm -rf ~$bmhc_data_2024.xlsx
# rm -rf ~$bmhc_q4_2024_cleaned2.xlsx