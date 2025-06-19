# Consumer Security Analysis V2

A comprehensive tool for analyzing consumer app reviews from Google Play Store and Apple App Store to extract security and privacy insights.

## 🔍 Overview

This project provides tools to:
- **Scrape** app reviews from Google Play Store and Apple App Store
- **Analyze** sentiment and extract security-related concerns
- **Visualize** trends and patterns in consumer feedback
- **Generate** interactive dashboards and word clouds
- **Export** filtered datasets for further analysis

## 🚀 Features

- ✅ **Multi-platform Support**: Google Play Store & Apple App Store
- ✅ **Sentiment Analysis**: VADER sentiment analysis for review classification
- ✅ **Interactive Visualizations**: Time-series plots, word clouds, and dynamic filters
- ✅ **Security Focus**: Keyword filtering for security and privacy concerns
- ✅ **Export Capabilities**: CSV downloads and data filtering
- ✅ **Jupyter Integration**: Interactive notebooks for analysis
- ✅ **Real-time Processing**: Live data collection and analysis

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yvh1223/consumer-security-analysis-v2.git
   cd consumer-security-analysis-v2
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Enable Jupyter widgets**
   ```bash
   jupyter nbextension enable --py widgetsnbextension --sys-prefix
   ```

5. **Set up environment variables** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if needed
   ```

## 📊 Usage

### Command Line Interface

#### Fetch Google Play Store Reviews
```bash
python src/data_collection/fetch_reviews.py \
    --platform google \
    --app_id com.wsandroid.suite \
    --country us \
    --max_reviews 1000
```

#### Fetch Apple App Store Reviews
```bash
python src/data_collection/fetch_reviews.py \
    --platform apple \
    --app_id 724596345 \
    --country us \
    --max_reviews 500
```

### Jupyter Notebook Analysis

1. **Start Jupyter**
   ```bash
   jupyter notebook
   ```

2. **Open the analysis notebook**
   ```
   notebooks/interactive_sentiment.ipynb
   ```

3. **Features include:**
   - 📊 Time-series sentiment analysis
   - ☁️ Dynamic word clouds
   - 🔍 Interactive filtering
   - 📥 CSV export functionality
   - 📈 Trend visualization

## 📁 Project Structure

```
consumer-security-analysis-v2/
├── src/
│   └── data_collection/
│       └── fetch_reviews.py          # Review scraping script
├── notebooks/
│   ├── interactive_sentiment.ipynb   # Main analysis notebook
│   └── data/
│       └── raw/                      # Raw data storage
├── requirements.txt                  # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following (optional):

```bash
# API Keys (if needed for enhanced features)
OPENAI_API_KEY=your_openai_key_here

# Analysis Settings
MAX_REVIEWS_DEFAULT=1000
DEFAULT_COUNTRY=us
```

### App IDs

Common app IDs for testing:
- **Google Play**: `com.wsandroid.suite` (Wise)
- **Apple App Store**: `724596345` (Wise)

## 📈 Analysis Features

### Sentiment Analysis
- **VADER Sentiment**: Specialized for social media text
- **Compound Scores**: -1 (negative) to +1 (positive)
- **Time-series Analysis**: Track sentiment trends over time

### Security Focus
- **Keyword Filtering**: Security, privacy, data, breach, hack, etc.
- **Pattern Recognition**: Identify common security concerns
- **Trend Analysis**: Monitor security perception changes

### Visualization Options
- **Interactive Plots**: Plotly-powered dashboards
- **Word Clouds**: Visual representation of common terms
- **Time Sliders**: Filter by date ranges
- **Export Tools**: Download filtered data

## 🎯 Use Cases

1. **Security Research**: Analyze user-reported security issues
2. **Competitive Analysis**: Compare security perceptions across apps
3. **Trend Monitoring**: Track security sentiment over time
4. **Product Management**: Understand user security concerns
5. **Academic Research**: Study consumer security awareness

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

- **Rate Limiting**: Be respectful of app store APIs and implement appropriate delays
- **Terms of Service**: Ensure compliance with Google Play and Apple App Store terms
- **Data Privacy**: Handle scraped data responsibly and in accordance with privacy laws
- **Research Use**: This tool is intended for research and analysis purposes

## 🐛 Troubleshooting

### Common Issues

1. **Installation Problems**
   ```bash
   # Try upgrading pip
   pip install --upgrade pip
   
   # Install packages individually if bulk install fails
   pip install google-play-scraper app-store-web-scraper pandas
   ```

2. **Jupyter Widget Issues**
   ```bash
   # Reinstall jupyter widgets
   pip install --upgrade ipywidgets
   jupyter nbextension enable --py widgetsnbextension
   ```

3. **Apple App Store Scraping**
   - Some apps may have limited review access
   - Try different country codes if reviews aren't available
   - Respect rate limits to avoid IP blocking

## 📞 Support

For questions, issues, or feature requests:
- 📧 Create an [Issue](https://github.com/yvh1223/consumer-security-analysis-v2/issues)
- 💬 Start a [Discussion](https://github.com/yvh1223/consumer-security-analysis-v2/discussions)

---

**Made with ❤️ for consumer security research**
