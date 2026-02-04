# 🎬 Pulse of Public

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)
![AI Powered](https://img.shields.io/badge/AI-Gemini%201.5-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**Transform YouTube comments into actionable creator insights with AI**

A modern, AI-powered analytics platform that helps YouTube creators understand their audience sentiment, identify improvement opportunities, and make data-driven content decisions.

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Tech Stack](#-tech-stack)

</div>

---

## ✨ Features

### 🎯 AI-Powered Insights
- **Smart Analysis**: Gemini AI generates human-readable insights from comments
- **Actionable Recommendations**: Get specific improvement suggestions for your content
- **Sentiment Understanding**: Know what viewers love and what frustrates them

### 📊 Modern Dashboard
- **Dark Theme SaaS Design**: Professional glassmorphism UI
- **Tab-Based Navigation**: Intuitive interface with Overview, Insights, Comments, and Analytics
- **Real-Time Metrics**: Engagement rate, sentiment distribution, and key statistics
- **Interactive Charts**: Modern visualizations with Plotly

### 💬 Advanced Comment Analysis
- **Search & Filter**: Find specific comments by keyword or sentiment
- **Metadata Rich**: Includes likes, timestamps, and reply counts
- **Export Ready**: Download all data as CSV for reports

### 🚀 Production Ready
- **Session Management**: Smooth tab navigation without re-analysis
- **Progress Tracking**: Multi-stage loading indicators
- **Error Handling**: Graceful failure with user-friendly messages
- **API Optimization**: Smart pagination to manage YouTube API quotas

---

## 🖼️ Demo

### Landing Page
Clean, modern interface with glassmorphism design and clear call-to-action.

### Dashboard Views
- **Overview Tab**: Video preview, channel stats, sentiment metrics
- **Insights Tab**: AI-generated recommendations and analysis
- **Comments Tab**: Searchable comment explorer
- **Analytics Tab**: Interactive charts and visualizations

---

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- YouTube Data API v3 key
- Google Gemini API key (optional, for AI insights)

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd P_o_P
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Keys

⚠️ **SECURITY WARNING**: Never commit API keys to version control!

#### Option 1: Copy from examples (Recommended)
```bash
# Copy example files and fill in your keys
cp .env.example .env
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

#### Option 2: Create manually

Create `.env` file in the project root:
```env
# Google Gemini API Key - Get from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here
```

Create `.streamlit/secrets.toml`:
```toml
[default]
# YouTube Data API Key - Get from: https://console.cloud.google.com/apis/credentials
DEVELOPER_KEY = "your_youtube_api_key_here"
```

**✅ These files are already in `.gitignore` and won't be committed**

### Step 4: Run the Application
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📖 Usage

### 1. Analyze a Video
1. Paste a YouTube video URL in the sidebar
2. Click **"🚀 Analyze Video"**
3. Wait for the analysis to complete (5-30 seconds)

### 2. Explore Results

#### Overview Tab
- View video preview and channel information
- Check key metrics (views, likes, comments, engagement rate)
- See sentiment distribution breakdown

#### Insights Tab
- Read AI-generated insights about what viewers loved
- Understand common complaints and concerns
- Get actionable recommendations for improvement
- Review overall sentiment summary

#### Comments Tab
- Search comments by keyword
- Filter by sentiment (Positive, Negative, Neutral)
- Sort by various criteria
- Export data as CSV

#### Analytics Tab
- View horizontal bar chart of sentiment distribution
- Analyze donut chart showing percentages
- Download visualizations

---

## 🏗️ Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **Streamlit**: Web application framework
- **NLTK + VADER**: Sentiment analysis engine
- **Google AI (Gemini)**: Natural language insights generation

### Data & APIs
- **YouTube Data API v3**: Video and comment data
- **Pandas**: Data manipulation and analysis
- **CSV**: Data storage and export

### Frontend
- **Custom CSS**: Glassmorphism design system
- **Plotly**: Interactive data visualizations
- **Google Fonts (Inter)**: Professional typography

### Configuration
- **python-dotenv**: Environment variable management
- **Streamlit Secrets**: API key management

---

## 📁 Project Structure

```
P_o_P/
├── app.py                      # Main Streamlit application
├── Senti.py                    # Sentiment analysis logic
├── YoutubeCommentScrapper.py   # YouTube API integration
├── style.css                   # Custom CSS styling
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in repo)
├── .streamlit/
│   ├── config.toml            # Streamlit configuration
│   └── secrets.toml           # API keys (not in repo)
├── LOGO.png                   # Application logo
└── README.md                  # This file
```

---

## 🎨 Design System

### Color Palette
```css
Background:   #0a0e1a → #1a1f35 (gradient)
Cards:        rgba(255,255,255,0.05) + backdrop-blur(20px)
Accent:       #6366f1 (Indigo)
Success:      #10b981 (Green)
Danger:       #ef4444 (Red)
```

### Typography
- **Primary**: Inter (Google Fonts)
- **Weights**: 300, 400, 500, 600, 700
- **Code**: JetBrains Mono

---

## 🔑 Getting API Keys

### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Create credentials (API Key)
5. Copy the key to `.streamlit/secrets.toml`

### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Copy the key to `.env` file

---

## 🔒 Security

### Protected Files
The following files containing sensitive information are **automatically ignored** by Git:

```
.env                        # Gemini API key
.streamlit/secrets.toml     # YouTube API key
*.csv                       # Scraped comment data
*.log                       # Log files
```

### Best Practices
1. ✅ **Use `.env.example` files**: Commit example configs, never actual keys
2. ✅ **Verify `.gitignore`**: Check sensitive files aren't tracked
3. ✅ **Rotate keys regularly**: Change API keys periodically
4. ✅ **Restrict API keys**: Use API restrictions in Google Cloud Console
5. ⚠️ **Never share keys**: Don't paste keys in issues, chat, or screenshots

### Check Before Committing
```bash
# Verify no sensitive files will be committed
git status

# Check what's ignored
git check-ignore -v .env .streamlit/secrets.toml
```

---

## 📊 Features Breakdown

| Feature | Status | Description |
|---------|--------|-------------|
| YouTube Integration | ✅ | Fetch video metadata and comments |
| Sentiment Analysis | ✅ | VADER-based sentiment scoring |
| AI Insights | ✅ | Gemini-powered recommendations |
| Dark Theme UI | ✅ | Glassmorphism SaaS design |
| Tab Navigation | ✅ | Overview, Insights, Comments, Analytics |
| Comment Search | ✅ | Keyword-based filtering |
| Interactive Charts | ✅ | Plotly visualizations |
| CSV Export | ✅ | Download comment data |
| Progress Indicators | ✅ | Multi-stage loading feedback |

---

## 🚀 Roadmap

### Planned Enhancements
- [ ] Toxicity detection (spam, hate speech, profanity)
- [ ] Sentiment timeline over video duration
- [ ] Keyword/topic extraction cloud
- [ ] PDF report generation
- [ ] Video comparison mode
- [ ] Email digest for creators
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **VADER Sentiment Analysis**: NLTK library
- **Google AI**: Gemini API for natural language generation
- **YouTube**: Data API v3 for video and comment data
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations

---

## 📧 Contact

For questions, feedback, or support:
- Open an issue on GitHub
- Email: [Your Email]
- Portfolio: [Your Website]

---

<div align="center">

**Made with ❤️ for YouTube Creators**

⭐ Star this repo if you found it helpful!

</div>
