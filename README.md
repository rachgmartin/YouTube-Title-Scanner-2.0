# YouTube Title Scanner App

This app scans video titles from a specified YouTube channel to identify potentially advertiser-unfriendly content based on YouTube's advertiser guidelines. It uses keyword matching, context awareness, and severity scoring to flag and suggest safer alternatives.

## Features
- Fetches video titles via YouTube Data API
- Flags sensitive or inappropriate terms
- Applies context-aware scoring
- Outputs Excel reports
- Includes CSS classes for a duotone image filter
- Provides responsive aspect-ratio helpers (1:1, 4:3, 16:9)
- Built-in dark mode styling

## Setup
1. Install requirements:
   ```
   pip install -r requirements.txt
   ```
2. Copy `env.example` to `.env` and add your API key:
   ```bash
   cp env.example .env
   echo "YOUTUBE_API_KEY=your_api_key_here" >> .env
   ```

The app reads environment variables from this `.env` file on startup.

## Run the app
```bash
streamlit run app.py
```

