# Atomberg  Agent

An autonomous AI-powered agent that monitors and analyzes brand presence across social media platforms (YouTube and X/Twitter) to calculate Share of Voice (SoV) and extract strategic customer insights.

## 🎯 Features

- **Multi-Platform Monitoring**: Scans YouTube and X (Twitter) for brand mentions and competitor activity
- **AI-Powered Analysis**: Uses Google Gemini to analyze sentiment, categorize content, and extract insights
- **Deep-Dive Capability**: Automatically identifies viral content and extracts comments for qualitative analysis
- **Share of Voice Calculation**: Quantifies brand visibility relative to competitors
- **Automated Reporting**: Generates markdown reports and JSON data exports

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser
- Google API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

**Windows:**
```cmd
setup.bat
```

**macOS/Linux:**
```bash
./setup.sh
```

### Configuration

Create a `.env` file in the project directory:
```env
api=YOUR_GOOGLE_API_KEY_HERE
```

### Running the Agent

**Windows:**
```cmd
.venv\Scripts\activate
python agent.py
```

**macOS/Linux:**
```bash
source .venv/bin/activate
python agent.py
```

## 📊 How It Works

### Phase 1: Multi-Platform Scanning
- **YouTube**: Searches for "smart fan review" and collects top 10 videos
- **X (Twitter)**: Searches for "smart fan" posts (requires manual login)
- Extracts: titles, engagement metrics, URLs, and content

### Phase 2: Deep Dive Analysis
- Identifies the most engaging Atomberg content
- Falls back to targeted search if none found in generic results
- Extracts comments/replies for Voice of Customer analysis

### Phase 3: Intelligence Report Generation
- Calculates Share of Voice (SoV) percentage
- Identifies viral dependency risks
- Extracts strategic insights (pricing sensitivity, feature preferences, quality concerns)
- Generates human-readable report + machine-readable JSON

## 📁 Output Files

After execution, you'll receive:

| File | Description |
|------|-------------|
| `Atomberg_Report.md` | Executive summary with strategic insights |
| `atomberg_feed_data.json` | Raw data from social media feeds |
| `atomberg_comments_data.json` | Deep-dive comments and replies |

## 🛠️ Technology Stack

- **Web Automation**: Selenium + Undetected ChromeDriver
- **AI Engine**: Google Gemini 2.0 (via LangChain)
- **Data Processing**: Pandas, NumPy
- **NLP**: TextBlob (fallback sentiment analysis)

## 📋 Requirements

See `requirements.txt` for full dependency list:
- pandas
- numpy
- python-dotenv
- selenium
- undetected-chromedriver
- textblob
- langchain-google-genai
- langchain-core
- setuptools

## ⚠️ Important Notes

1. **Do NOT close the Chrome window** that opens during execution
2. **Manual login required** for X/Twitter scraping
3. Chrome browser must be up to date
4. The agent respects platform rate limits with built-in delays

## 🐛 Troubleshooting

**Browser closes immediately:**
- Ensure Chrome is updated to the latest version
- Run: `pip install --upgrade undetected-chromedriver`

**API Key errors:**
- Verify your `.env` file exists and is properly formatted
- Check API key validity at [Google AI Studio](https://aistudio.google.com/app/apikey)

**Module not found:**
- Ensure virtual environment is activated
- Re-run: `pip install -r requirements.txt`

For detailed setup instructions, see [README_SETUP.md](README_SETUP.md)


## 👥 Authors

- Prathamesh Lohar
- For Atomberg Technologies Team

---

**Last Updated**: December 2025
