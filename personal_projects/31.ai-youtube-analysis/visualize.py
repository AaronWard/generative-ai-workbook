import json
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict
from datetime import datetime

# Load the JSON data
with open('data/vrsen.json', 'r') as file:
    data = json.load(file)

# List of specified categories
specified_categories = [
    "In context learning",
    "Multimodal models", 
    "Agents",
    "Vector Databases",
    "Prompting",
    "Chain of thought reasoning",
    "Image",
    "Search", 
    "Classification",
    "Topic Modelling",
    "Clustering",
    "Data, Text and Code generation",
    "Summarization",
    "Rewriting",
    "Extractions", 
    "Proof reading",
    "Swarms",
    "Querying Data",
    "Fine tuning",
    "Executing code",
    "Sentiment Analysis",
    "Planning and Complex Reasoning",
    "Image classification and generation (If multi-modal)",
    "Philosophical reasoning and ethics",
    "Reinforcement learning",
    "Model security and privacy",
    "APIs",
    "Infrastructure"
]

# Prepare a dictionary to hold category counts over time
category_counts = defaultdict(lambda: defaultdict(int))

# Process the data
for entry in data:
    date = datetime.strptime(entry['published_at'], '%Y-%m-%dT%H:%M:%SZ').date()
    for category in entry['categories']:
        if category in specified_categories:
            category_counts[category][date] += 1

# Convert the dictionary to a DataFrame
df = pd.DataFrame(category_counts).fillna(0)

# Convert the index to a DatetimeIndex
df.index = pd.to_datetime(df.index, errors='coerce')

# Sort the DataFrame by date
df = df.sort_index()

# df = df.cumsum()

# Group by week
df = df.resample('W').sum()

# Reset index to have date as a column for plotly
df = df.reset_index().melt(id_vars='index', var_name='Category', value_name='Cumulative Frequency')
df.rename(columns={'index': 'Date'}, inplace=True)

# Create a plotly figure
fig = go.Figure()

# Add a line for each category
for category in specified_categories:
    category_data = df[df['Category'] == category]
    fig.add_trace(go.Bar(
        x=category_data['Date'],
        y=category_data['Cumulative Frequency'],
        name=category,
        hoverinfo='x+y+name'
    ))

# Update layout for better visualization
fig.update_layout(
    title='Specified Category Frequency Over Time (Weekly)',
    xaxis_title='Date',
    yaxis_title='Cumulative Frequency',
    legend_title='Category',
    hovermode='x',  # Show tooltips only when hovering over specific lines
    transition=dict(duration=500),  # Add transitions
    showlegend=True,
    barmode='stack'  # Set barmode to 'stack' for stacked bars
)

# Show the plot
fig.show()