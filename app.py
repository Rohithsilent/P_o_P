import streamlit as st
import os
import pandas as pd
from Senti import extract_video_id, analyze_sentiment, bar_chart, plot_sentiment
from YoutubeCommentScrapper import save_video_comments_to_csv, get_channel_info, youtube, get_channel_id, get_video_stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline

# Set Hugging Face API key
os.environ["HUGGINGFACE_API_KEY"] = "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"

qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-small")

def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))

def find_relevant_comments(user_query, comments, top_n=5, sentiment_filter=None):
    """Finds top_n most relevant comments to the user query with optional sentiment filtering."""
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(comments)
    query_vector = vectorizer.transform([user_query])
    cosine_similarities = cosine_similarity(query_vector, tfidf_matrix)
    # Get indices of top_n most similar comments
    top_indices = cosine_similarities.argsort()[0][-top_n:][::-1]
    relevant_comments = [comments[idx] for idx in top_indices]
    
    # Apply sentiment filter (if provided)
    if sentiment_filter:
        # Filter the comments by sentiment (negative, positive, neutral)
        relevant_comments = [comment for comment in relevant_comments if sentiment_filter(comment)]
    
    return relevant_comments

def categorize_question(user_query):
    keywords_comments = ['comment', 'opinion', 'thoughts', 'say', 'feedback']
    keywords_channel = ['channel', 'subscriber', 'videos', 'date', 'created', 'description']
    keywords_video = ['views', 'likes', 'comments', 'stats', 'video']
    keywords_negative = ['negative', 'hate', 'bad', 'poor']

    if any(keyword in user_query.lower() for keyword in keywords_comments):
        return "comments"
    elif any(keyword in user_query.lower() for keyword in keywords_channel):
        return "channel_info"
    elif any(keyword in user_query.lower() for keyword in keywords_video):
        return "video_info"
    elif any(keyword in user_query.lower() for keyword in keywords_negative):
        return "negative_comments"
    else:
        return "unknown"

def get_general_answer(user_query):
    # Use Hugging Face model to get a response for general questions
    answer = qa_pipeline(user_query)
    return answer[0]['generated_text']

st.set_page_config(page_title='Synergy_Squad', page_icon='LOGO.png', initial_sidebar_state='auto')
st.sidebar.title("Sentimental Analysis")
st.sidebar.header("Enter YouTube Link")
youtube_link = st.sidebar.text_input("Link")
directory_path = os.getcwd()
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

if youtube_link:
    video_id = extract_video_id(youtube_link)
    channel_id = get_channel_id(video_id)
    if video_id:
        st.sidebar.write("The video ID is:", video_id)
        csv_file = save_video_comments_to_csv(video_id)
        delete_non_matching_csv_files(directory_path, video_id)
        st.sidebar.write("Comments saved to CSV!")
        st.sidebar.download_button(label="Download Comments", data=open(csv_file, 'rb').read(), file_name=os.path.basename(csv_file), mime="text/csv")

        # Using functions to get channel info
        channel_info = get_channel_info(youtube, channel_id)

        # Display channel information
        col1, col2 = st.columns(2)
        with col1:
            channel_logo_url = channel_info['channel_logo_url']
            st.image(channel_logo_url, width=250)

        with col2:
            channel_title = channel_info['channel_title']
            st.title(channel_title)

        st.title(" ")
        col3, col4, col5 = st.columns(3)
        with col3:
            video_count = channel_info['video_count']
            st.subheader("Total Videos")
            st.subheader(video_count)

        with col4:
            channel_created_date = channel_info['channel_created_date']
            created_date = channel_created_date[:10]
            st.subheader("Channel Created")
            st.subheader(created_date)

        with col5:
            st.subheader("Subscriber Count")
            st.subheader(channel_info["subscriber_count"])

        stats = get_video_stats(video_id)

        st.title("Video Information:")
        col6, col7, col8 = st.columns(3)
        with col6:
            st.subheader("Total Views")
            st.subheader(stats["viewCount"])

        with col7:
            st.subheader("Like Count")
            st.subheader(stats["likeCount"])

        with col8:
            st.subheader("Comment Count")
            st.subheader(stats["commentCount"])

        st.header(" ")
        _, container, _ = st.columns([10, 80, 10])
        container.video(data=youtube_link)

        results = analyze_sentiment(csv_file)

        col9, col10, col11 = st.columns(3)
        with col9:
            st.subheader("Positive Comments")
            st.subheader(results['num_positive'])

        with col10:
            st.subheader("Negative Comments")
            st.subheader(results['num_negative'])

        with col11:
            st.subheader("Neutral Comments")
            st.subheader(results['num_neutral'])

        bar_chart(csv_file)
        plot_sentiment(csv_file)

        st.subheader("Channel Description")
        channel_description = channel_info['channel_description']
        st.write(channel_description)

        # Chatbot Interface
        st.title("Ask a Question:")
        user_query = st.text_input("Ask something about the video or channel")
        if user_query:
            question_type = categorize_question(user_query)
            comments_df = pd.read_csv(csv_file)

            # Check if the 'comment' column exists
            if 'comment' in comments_df.columns or 'Comment' in comments_df.columns:
                if question_type == "comments":
                    comments = comments_df['comment'].tolist() if 'comment' in comments_df.columns else comments_df['Comment'].tolist()
                    relevant_comments = find_relevant_comments(user_query, comments, top_n=5)  # Adjust top_n as needed
                    st.write(f"**Chatbot Answer (Comments Related):**")
                    for comment in relevant_comments:
                        st.write(f"- {comment}")
                elif question_type == "negative_comments":
                    comments = comments_df['comment'].tolist() if 'comment' in comments_df.columns else comments_df['Comment'].tolist()
                    # Filter negative comments based on sentiment
                    relevant_comments = find_relevant_comments(user_query, comments, sentiment_filter=lambda x: 'negative' in analyze_sentiment(x).lower(), top_n=5)
                    st.write(f"**Chatbot Answer (Negative Comments):**")
                    for comment in relevant_comments:
                        st.write(f"- {comment}")
                elif question_type == "channel_info":
                    st.write(f"**Chatbot Answer (Channel Info Related):** {channel_info}")
                elif question_type == "video_info":
                    st.write(f"**Chatbot Answer (Video Info Related):** {stats}")
                else:
                    # Use Hugging Face model for general questions
                    general_answer = get_general_answer(user_query)
                    st.write(f"**Chatbot Answer (General Knowledge):** {general_answer}")
            else:
                # If the 'comment' column is missing, inform the user
                st.error("No 'comment' column found in the CSV file. Please make sure the comments are saved properly.")
