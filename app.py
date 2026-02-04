import logging
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import streamlit as st
import pandas as pd
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

load_dotenv()

# Set up Gemini API Key
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Initialize client
client = None
if gemini_api_key:
    try:
        client = genai.Client(api_key=gemini_api_key)
        logger.info("Gemini client initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing Gemini client: {e}")
else:
    logger.error("GEMINI_API_KEY is not set")

# Function to send messages to Gemini
def send_to_gemini(question, context=""):
    if not client:
        logger.error("Gemini client not initialized")
        return "AI insights unavailable. Please check API key configuration."
    
    logger.info(f"Sending request to Gemini. Question length: {len(question)}")
    try:
        full_prompt = f"{context}\n\n{question}"
        logger.info("Sending message to Gemini...")
        
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=2048,
            )
        )
        logger.info(f"Response received from Gemini. Length: {len(response.text)}")
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error occurred while contacting Gemini: {e}")
        return f"Error: {str(e)}"

# Function to delete non-matching CSV files
def delete_non_matching_csv_files(directory_path, video_id):
    logger.info(f"Deleting non-matching CSV files in {directory_path}")
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))
        logger.info(f"Deleted file: {file_name}")

# Function to load custom CSS
def load_custom_css():
    css_file = "style.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Function to create metric card HTML
def create_metric_card(label, value, icon="📊"):
    return f"""
    <div class="metric-card fade-in">
        <div class="metric-icon">{icon}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """

# Function to create insight card HTML
def create_insight_card(title, content, card_type="info", icon="💡"):
    import re
    # Convert markdown bold (**text**) to HTML <strong>
    formatted_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
    # Convert bullet points and newlines to proper HTML
    formatted_content = formatted_content.replace('\n- ', '<br>• ')
    formatted_content = formatted_content.replace('\n', '<br>')
    # Handle cases where content starts with a bullet
    if formatted_content.startswith('- '):
        formatted_content = '• ' + formatted_content[2:]
    
    return f"""
    <div class="insight-card {card_type} fade-in">
        <div class="insight-title">{icon} {title}</div>
        <div class="insight-content">{formatted_content}</div>
    </div>
    """

# Function to generate creator insights using Gemini
def generate_creator_insights(csv_file, sentiment_results, video_title):
    if not client:
        logger.warning("Gemini client not available for insights generation")
        return None
    
    try:
        # Read comments
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        comments_text = df['Comment'].tolist()
        
        # Sample comments for analysis (limit to avoid token limits)
        sample_size = min(50, len(comments_text))
        sampled_comments = comments_text[:sample_size]
        
        # Create a comprehensive prompt for single API call
        full_prompt = f"""
You are analyzing YouTube comments for the video: "{video_title}"

Sentiment Statistics:
- Positive: {sentiment_results['num_positive']} comments
- Negative: {sentiment_results['num_negative']} comments  
- Neutral: {sentiment_results['num_neutral']} comments

Sample Comments (first {sample_size}):
{chr(10).join([f"- {c[:200]}" for c in sampled_comments])}

Please provide insights in the following format:

## What Viewers Loved
[List 2-3 specific things viewers praised, in bullet points]

## Common Complaints
[List 2-3 specific concerns or criticisms, in bullet points]

## Recommendations
[List 2-3 actionable improvements for future videos, in bullet points]

## Summary
[2-3 sentences summarizing overall sentiment and key takeaway]
"""
        
        logger.info("Generating comprehensive insights in single API call...")
        response = send_to_gemini(full_prompt, "")
        
        if "Error" in response:
            logger.error(f"Gemini returned error: {response}")
            return None
        
        # Parse the response into sections
        insights = {}
        lines = response.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            if '## What Viewers Loved' in line or 'Loved' in line and '##' in line:
                if current_section and section_content:
                    insights[current_section] = '\n'.join(section_content).strip()
                current_section = 'loved'
                section_content = []
            elif '## Common Complaints' in line or 'Complaints' in line and '##' in line:
                if current_section and section_content:
                    insights[current_section] = '\n'.join(section_content).strip()
                current_section = 'complaints'
                section_content = []
            elif '## Recommendations' in line or 'Recommendations' in line and '##' in line:
                if current_section and section_content:
                    insights[current_section] = '\n'.join(section_content).strip()
                current_section = 'improvements'
                section_content = []
            elif '## Summary' in line or 'Summary' in line and '##' in line:
                if current_section and section_content:
                    insights[current_section] = '\n'.join(section_content).strip()
                current_section = 'summary'
                section_content = []
            elif current_section and line.strip():
                section_content.append(line)
        
        # Add last section
        if current_section and section_content:
            insights[current_section] = '\n'.join(section_content).strip()
        
        # Ensure all keys exist
        if 'loved' not in insights:
            insights['loved'] = "Viewers appreciated the content overall."
        if 'complaints' not in insights:
            insights['complaints'] = "No major complaints identified."
        if 'improvements' not in insights:
            insights['improvements'] = "Continue creating similar content."
        if 'summary' not in insights:
            insights['summary'] = f"Overall sentiment is {('positive' if sentiment_results['num_positive'] > sentiment_results['num_negative'] else 'mixed')}."
        
        logger.info("Insights generated successfully")
        return insights
        
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return None

# Function to generate basic insights from sentiment data when Gemini is unavailable
def generate_basic_insights(csv_file, sentiment_results):
    """Generate simple insights from sentiment distribution"""
    try:
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        total = sentiment_results['num_positive'] + sentiment_results['num_negative'] + sentiment_results['num_neutral']
        
        if total == 0:
            return None
        
        pos_pct = (sentiment_results['num_positive'] / total) * 100
        neg_pct = (sentiment_results['num_negative'] / total) * 100
        
        insights = {
            'loved': f'- {pos_pct:.1f}% of comments were positive\n- Viewers engaged positively with the content\n- Strong audience appreciation detected',
            'complaints': f'- {neg_pct:.1f}% of comments were negative\n- Some viewers expressed concerns\n- Review negative comments for specific issues' if neg_pct > 20 else '- Minimal negative feedback\n- Audience is generally satisfied\n- Keep up the good work!',
            'improvements': '- Analyze top negative comments manually\n- Respond to constructive criticism\n- Continue creating similar content',
            'summary': f'Your video received {pos_pct:.1f}% positive sentiment. ' + ('This is excellent! Viewers love your content.' if pos_pct > 70 else 'There is room for improvement based on audience feedback.' if pos_pct < 50 else 'The reception is good with balanced feedback.')
        }
        return insights
    except:
        return None

# Configure the Streamlit page
st.set_page_config(
    page_title='Pulse of Public',
    page_icon='LOGO.png',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Load custom CSS
load_custom_css()

# Initialize session state for tabs
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'Overview'

if 'video_data' not in st.session_state:
    st.session_state.video_data = None

# Sidebar
with st.sidebar:
    st.markdown('<h1 class="text-gradient">🎬 Pulse of Public</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: var(--text-secondary); font-size: 0.9rem;">Transform comments into actionable creator insights</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 📹 Analyze Video")
    youtube_link = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
    
    analyze_button = st.button("🚀 Analyze Video", use_container_width=True, type="primary")

# Main content area
if youtube_link and analyze_button:
    with st.spinner("🔄 Processing video..."):
        video_id = extract_video_id(youtube_link)
        if not video_id:
            st.error("❌ Invalid YouTube URL. Please enter a valid link.")
        else:
            logger.info(f"Extracted Video ID: {video_id}")
            
            # Create progress indicators
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Extract video metadata
            status_text.text("📥 Fetching video metadata...")
            progress_bar.progress(20)
            
            channel_id = get_channel_id(video_id)
            video_stats = get_video_stats(video_id)
            channel_info = get_channel_info(youtube, channel_id)
            
            # Step 2: Fetch comments
            status_text.text("💬 Fetching comments...")
            progress_bar.progress(40)
            
            csv_file = save_video_comments_to_csv(video_id)
            directory_path = os.getcwd()
            delete_non_matching_csv_files(directory_path, video_id)
            
            # Step 3: Analyze sentiment
            status_text.text("🧠 Analyzing sentiment...")
            progress_bar.progress(60)
            
            sentiment_results = analyze_sentiment(csv_file)
            
            # Step 4: Generate insights (if Gemini is available)
            status_text.text("✨ Generating AI insights...")
            progress_bar.progress(80)
            
            insights = None
            if gemini_api_key:
                # Get video title from API
                video_request = youtube.videos().list(part='snippet', id=video_id).execute()
                video_title = video_request['items'][0]['snippet']['title']
                insights = generate_creator_insights(csv_file, sentiment_results, video_title)
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            
            # Store data in session state
            st.session_state.video_data = {
                'video_id': video_id,
                'video_stats': video_stats,
                'channel_info': channel_info,
                'sentiment_results': sentiment_results,
                'csv_file': csv_file,
                'youtube_link': youtube_link,
                'insights': insights
            }
            
            st.success("✅ Video analyzed successfully!")
            st.balloons()

# Display results if data exists
if st.session_state.video_data:
    data = st.session_state.video_data
    
    # Tab navigation
    st.markdown('<div class="custom-tabs">', unsafe_allow_html=True)
    cols = st.columns(4)
    tabs = ['Overview', 'Insights', 'Comments', 'Analytics']
    
    for idx, tab in enumerate(tabs):
        with cols[idx]:
            active_class = 'active' if st.session_state.current_tab == tab else ''
            if st.button(f"{'📊' if tab == 'Overview' else '💡' if tab == 'Insights' else '💬' if tab == 'Comments' else '📈'} {tab}", key=f"tab_{tab}", use_container_width=True):
                st.session_state.current_tab = tab
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # OVERVIEW TAB
    if st.session_state.current_tab == 'Overview':
        # Video preview section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.video(data['youtube_link'])
        
        with col2:
            # Channel info
            channel_logo_url = data['channel_info'].get('channel_logo_url', '')
            if channel_logo_url:
                st.image(channel_logo_url, width=80)
            st.markdown(f"### {data['channel_info'].get('channel_title', 'N/A')}")
            st.markdown(f"**Subscribers:** {data['channel_info'].get('subscriber_count', 'N/A'):,}" if isinstance(data['channel_info'].get('subscriber_count'), int) else f"**Subscribers:** {data['channel_info'].get('subscriber_count', 'N/A')}")
        
        st.markdown("### 📊 Key Metrics")
        
        # Video metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            views = data['video_stats'].get('viewCount', 0)
            st.markdown(create_metric_card("Total Views", f"{int(views):,}" if views != 'N/A' else 'N/A', "👁️"), unsafe_allow_html=True)
        
        with col2:
            likes = data['video_stats'].get('likeCount', 0)
            st.markdown(create_metric_card("Likes", f"{int(likes):,}" if likes != 'N/A' else 'N/A', "👍"), unsafe_allow_html=True)
        
        with col3:
            comments = data['video_stats'].get('commentCount', 0)
            st.markdown(create_metric_card("Comments", f"{int(comments):,}" if comments != 'N/A' else 'N/A', "💬"), unsafe_allow_html=True)
        
        with col4:
            # Calculate engagement rate
            if views and views != 'N/A' and likes and likes != 'N/A':
                engagement = (int(likes) / int(views)) * 100
                st.markdown(create_metric_card("Engagement", f"{engagement:.2f}%", "📈"), unsafe_allow_html=True)
            else:
                st.markdown(create_metric_card("Engagement", "N/A", "📈"), unsafe_allow_html=True)
        
        st.markdown("### 😊 Sentiment Distribution")
        
        col1, col2, col3 = st.columns(3)
        
        total = data['sentiment_results']['num_positive'] + data['sentiment_results']['num_negative'] + data['sentiment_results']['num_neutral']
        
        with col1:
            positive_pct = (data['sentiment_results']['num_positive'] / total * 100) if total > 0 else 0
            st.markdown(create_metric_card("Positive", f"{positive_pct:.1f}%", "😊"), unsafe_allow_html=True)
        
        with col2:
            neutral_pct = (data['sentiment_results']['num_neutral'] / total * 100) if total > 0 else 0
            st.markdown(create_metric_card("Neutral", f"{neutral_pct:.1f}%", "😐"), unsafe_allow_html=True)
        
        with col3:
            negative_pct = (data['sentiment_results']['num_negative'] / total * 100) if total > 0 else 0
            st.markdown(create_metric_card("Negative", f"{negative_pct:.1f}%", "😠"), unsafe_allow_html=True)
        
        # Download CSV
        st.markdown("---")
        with open(data['csv_file'], 'rb') as f:
            st.download_button(
                label="📥 Download Comments CSV",
                data=f,
                file_name=os.path.basename(data['csv_file']),
                mime="text/csv",
                use_container_width=True
            )
    
    # INSIGHTS TAB
    elif st.session_state.current_tab == 'Insights':
        st.markdown("### ✨ Creator Insights")
        
        if data['insights']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(create_insight_card(
                    "What Viewers Loved Most",
                    data['insights']['loved'],
                    "success",
                    "🎯"
                ), unsafe_allow_html=True)
                
                st.markdown(create_insight_card(
                    "Actionable Recommendations",
                    data['insights']['improvements'],
                    "info",
                    "💡"
                ), unsafe_allow_html=True)
            
            with col2:
                st.markdown(create_insight_card(
                    "Common Complaints & Concerns",
                    data['insights']['complaints'],
                    "warning",
                    "⚠️"
                ), unsafe_allow_html=True)
                
                st.markdown(create_insight_card(
                    "Overall Sentiment Summary",
                    data['insights']['summary'],
                    "info",
                    "📊"
                ), unsafe_allow_html=True)
        else:
            # Try to generate basic insights from sentiment data
            basic_insights = generate_basic_insights(data['csv_file'], data['sentiment_results'])
            
            if basic_insights:
                st.warning("⚠️ AI-powered insights unavailable. Showing basic sentiment analysis instead.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(create_insight_card(
                        "Positive Feedback",
                        basic_insights['loved'],
                        "success",
                        "📊"
                    ), unsafe_allow_html=True)
                    
                    st.markdown(create_insight_card(
                        "Improvement Areas",
                        basic_insights['improvements'],
                        "info",
                        "💡"
                    ), unsafe_allow_html=True)
                
                with col2:
                    st.markdown(create_insight_card(
                        "Negative Feedback",
                        basic_insights['complaints'],
                        "warning",
                        "⚠️"
                    ), unsafe_allow_html=True)
                    
                    st.markdown(create_insight_card(
                        "Overall Summary",
                        basic_insights['summary'],
                        "info",
                        "📊"
                    ), unsafe_allow_html=True)
                
                # Show help message
                with st.expander("🔧 How to Enable AI-Powered Insights"):
                    st.markdown("""
                    **AI-powered insights are currently unavailable.** To enable advanced insights:
                    
                    1. Make sure `GEMINI_API_KEY` is set in your `.env` file
                    2. Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
                    3. Restart the Streamlit app
                    
                    **Current Issue**: The Gemini model may not be available with your API key.
                    
                    **Troubleshooting**:
                    - Check terminal logs for error messages
                    - Ensure your API key has Gemini API access enabled
                    - Try regenerating your API key
                    """)
            else:
                st.error("Unable to generate insights. Please check your data.")
    
    # COMMENTS TAB
    elif st.session_state.current_tab == 'Comments':
        st.markdown("### 💬 Comment Explorer")
        
        # Load comments
        df = pd.read_csv(data['csv_file'], encoding='utf-8-sig')
        
        # Add sentiment analysis to comments
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sid = SentimentIntensityAnalyzer()
        
        def get_sentiment(comment):
            scores = sid.polarity_scores(str(comment))
            if scores['compound'] > 0.05:
                return 'Positive'
            elif scores['compound'] < -0.05:
                return 'Negative'
            else:
                return 'Neutral'
        
        df['Sentiment'] = df['Comment'].apply(get_sentiment)
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_query = st.text_input("🔍 Search comments", placeholder="Type to search...", key="comment_search")
        
        with col2:
            sentiment_filter = st.selectbox("Filter by Sentiment", ["All", "Positive", "Negative", "Neutral"], key="sentiment_filter")
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Most Recent", "Most Liked", "Username"], key="sort_by")
        
        # Filter comments
        filtered_comments = df.copy()
        
        if search_query:
            filtered_comments = filtered_comments[filtered_comments['Comment'].str.contains(search_query, case=False, na=False)]
        
        if sentiment_filter != "All":
            filtered_comments = filtered_comments[filtered_comments['Sentiment'] == sentiment_filter]
        
        # Sort comments
        if sort_by == "Most Liked" and 'Likes' in filtered_comments.columns:
            filtered_comments = filtered_comments.sort_values('Likes', ascending=False)
        elif sort_by == "Username":
            filtered_comments = filtered_comments.sort_values('Username')
        
        st.markdown(f"**Showing {len(filtered_comments)} of {len(df)} comments**")
        
        # Display comments
        for idx, row in filtered_comments.head(50).iterrows():
            sentiment_class = row['Sentiment'].lower()
            likes_text = f" · {row['Likes']} likes" if 'Likes' in row and pd.notna(row['Likes']) and row['Likes'] > 0 else ""
            
            comment_html = f"""
            <div class="comment-card">
                <div class="comment-header">
                    <span class="comment-author">{row['Username']}</span>
                    <span class="comment-sentiment {sentiment_class}">{row['Sentiment']}</span>
                </div>
                <div class="comment-text">{row['Comment']}</div>
                <div class="comment-meta">
                    <span>{sentiment_class.capitalize()}{likes_text}</span>
                </div>
            </div>
            """
            st.markdown(comment_html, unsafe_allow_html=True)
        
        if len(filtered_comments) > 50:
            st.info(f"Showing first 50 comments. {len(filtered_comments) - 50} more available.")
    
    # ANALYTICS TAB
    elif st.session_state.current_tab == 'Analytics':
        st.markdown("### 📈 Sentiment Analytics")
        st.markdown('<p style="color: var(--text-secondary); margin-bottom: 2rem;">Visualize comment sentiment patterns and distribution</p>', unsafe_allow_html=True)
        
        # Bar Chart Section
        st.markdown("""
        <div class="analytics-section">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">
                📊 Sentiment Breakdown
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        bar_chart(data['csv_file'])
        
        st.markdown('<div style="height: 2rem;"></div>', unsafe_allow_html=True)
        
        # Pie Chart Section
        st.markdown("""
        <div class="analytics-section">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem; font-size: 1.1rem; font-weight: 600;">
                🥧 Sentiment Distribution
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        plot_sentiment(data['csv_file'])

else:
    # Beautiful Landing Page
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="margin-bottom: 2rem; animation: fadeIn 1s ease-out;">
            <h1 style="font-size: 3.5rem; margin-bottom: 0.5rem; background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">
                🎬 Pulse of Public
            </h1>
            <p style="font-size: 1.3rem; color: #cbd5e1; margin-top: 0.5rem; font-weight: 300;">
                Transform Comments into Creator Gold
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards in a grid
    st.markdown('<div style="max-width: 1200px; margin: 0 auto;">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem; height: 100%; transition: transform 0.3s ease;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">AI-Powered Insights</h3>
            <p style="color: #cbd5e1; line-height: 1.8;">
                Gemini AI analyzes thousands of comments to give you actionable recommendations and clear improvement areas.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem; height: 100%; transition: transform 0.3s ease;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">Real-Time Analytics</h3>
            <p style="color: #cbd5e1; line-height: 1.8;">
                Visualize sentiment distribution, engagement metrics, and audience reactions with interactive charts and insights.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 2rem; height: 100%; transition: transform 0.3s ease;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔍</div>
            <h3 style="color: #f8fafc; margin-bottom: 1rem;">Smart Comment Explorer</h3>
            <p style="color: #cbd5e1; line-height: 1.8;">
                Search, filter by sentiment, and discover patterns in your audience feedback instantly.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # How it works section
    st.markdown('<div style="margin-top: 3rem; text-align: center;">', unsafe_allow_html=True)
    st.markdown("""
    <h2 style="color: #f8fafc; margin-bottom: 2rem; font-size: 2rem;">How It Works</h2>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; color: white;">1</div>
            <h4 style="color: #f8fafc; margin-bottom: 0.5rem;">Paste URL</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Enter any YouTube video link</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; color: white;">2</div>
            <h4 style="color: #f8fafc; margin-bottom: 0.5rem;">AI Analysis</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">We analyze all comments</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; color: white;">3</div>
            <h4 style="color: #f8fafc; margin-bottom: 0.5rem;">Get Insights</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Receive actionable recommendations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem;">
            <div style="width: 60px; height: 60px; margin: 0 auto 1rem; background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 700; color: white;">4</div>
            <h4 style="color: #f8fafc; margin-bottom: 0.5rem;">Improve Content</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Create better videos</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CTA
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(129, 140, 248, 0.1) 100%); border-radius: 1rem; border: 1px solid rgba(99, 102, 241, 0.2);">
        <h3 style="color: #f8fafc; margin-bottom: 1rem;">Ready to Understand Your Audience?</h3>
        <p style="color: #cbd5e1; font-size: 1.1rem; margin-bottom: 1.5rem;">Enter a YouTube URL in the sidebar to get started →</p>
        <div style="display: inline-flex; gap: 1rem; align-items: center;">
            <span style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 600;">✓ Free to Use</span>
            <span style="background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 600;">✓ AI-Powered</span>
            <span style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.9rem; font-weight: 600;">✓ Instant Results</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
