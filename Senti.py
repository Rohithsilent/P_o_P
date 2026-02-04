import csv
import re
import pandas as pd
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import plotly.express as px
import plotly.graph_objects as go
from colorama import Fore, Style
from typing import Dict
import streamlit as st

def extract_video_id(youtube_link):
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None

def analyze_sentiment(csv_file):
    # Initialize the sentiment analyzer
    sid = SentimentIntensityAnalyzer()

    # Read in the YouTube comments from the CSV file
    comments = []
    with open(csv_file, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            comments.append(row['Comment'])

    # Count the number of neutral, positive, and negative comments
    num_neutral = 0
    num_positive = 0
    num_negative = 0
    for comment in comments:
        sentiment_scores = sid.polarity_scores(comment)
        if sentiment_scores['compound'] == 0.0:
            num_neutral += 1
        elif sentiment_scores['compound'] > 0.0:
            num_positive += 1
        else:
            num_negative += 1

    # Return the results as a dictionary
    results = {'num_neutral': num_neutral, 'num_positive': num_positive, 'num_negative': num_negative}
    return results

def bar_chart(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Create a Pandas DataFrame with the results
    df = pd.DataFrame({
        'Sentiment': ['Positive', 'Negative', 'Neutral'],
        'Number of Comments': [num_positive, num_negative, num_neutral]
    })

    # Create the horizontal bar chart using Plotly Express with modern dark theme
    fig = px.bar(df, y='Sentiment', x='Number of Comments', 
                 color='Sentiment', 
                 color_discrete_map={
                     'Positive': '#10b981',
                     'Negative': '#ef4444',
                     'Neutral': '#6b7280'
                 },
                 orientation='h')
    
    # Update layout for modern dark theme with responsive sizing
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#cbd5e1', size=13),
        xaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            title='Number of Comments',
            title_font=dict(color='#cbd5e1', size=14),
            tickfont=dict(color='#cbd5e1')
        ),
        yaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            title='',
            title_font=dict(color='#cbd5e1'),
            tickfont=dict(color='#cbd5e1', size=14)
        ),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=350,
        hovermode='y unified'
    )
    
    # Update traces for better appearance
    fig.update_traces(
        marker=dict(
            line=dict(width=0)
        ),
        texttemplate='%{x}',
        textposition='outside',
        textfont=dict(size=14, color='#cbd5e1')
    )

    # Show the chart with responsive container
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})    
    
def plot_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

    # Plot the pie chart with modern colors
    labels = ['Positive', 'Negative', 'Neutral']
    values = [num_positive, num_negative, num_neutral]
    colors = ['#10b981', '#ef4444', '#6b7280']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        textinfo='label+percent',
        textfont=dict(size=14, color='#f8fafc'),
        marker=dict(colors=colors, line=dict(color='#0a0e1a', width=2)),
        hole=0.4  # Donut chart for modern look
    )])
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=14, family='Inter, sans-serif', color='#cbd5e1'),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0)',
            font=dict(color='#cbd5e1', size=13),
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=10, r=10, t=10, b=40),
        height=400,
        hovermode='closest'
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    
    
def create_scatterplot(csv_file: str, x_column: str, y_column: str) -> None:
    # Load data from CSV
    data = pd.read_csv(csv_file)

    # Create scatter plot using Plotly
    fig = px.scatter(data, x=x_column, y=y_column, color='Category')

    # Customize layout
    fig.update_layout(
        title='Scatter Plot',
        xaxis_title=x_column,
        yaxis_title=y_column,
        font=dict(size=18)
    )

    # Display plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    
    
def print_sentiment(csv_file: str) -> None:
    # Call analyze_sentiment function to get the results
    results: Dict[str, int] = analyze_sentiment(csv_file)

    # Get the counts for each sentiment category
    num_neutral = results['num_neutral']
    num_positive = results['num_positive']
    num_negative = results['num_negative']

  
    # Determine the overall sentiment
    if num_positive > num_negative:
        overall_sentiment = 'POSITIVE'
        color = Fore.GREEN
    elif num_negative > num_positive:
        overall_sentiment = 'NEGATIVE'
        color = Fore.RED
    else:
        overall_sentiment = 'NEUTRAL'
        color = Fore.YELLOW

    # Print the overall sentiment in color
    print('\n'+ Style.BRIGHT+ color + overall_sentiment.upper().center(50, ' ') + Style.RESET_ALL)



