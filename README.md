# YouTube Title Scanner App

This app scans video titles from a specified YouTube channel to identify potentially advertiser-unfriendly content based on YouTube's advertiser guidelines. It uses keyword matching, context awareness, and severity scoring to flag and suggest safer alternatives.

## Features
- Fetches video titles via YouTube Data API
- Flags sensitive or inappropriate terms
- Applies context-aware scoring
- Outputs Excel reports

## Setup
1. Install requirements:
   ```
   pip install -r requirements.txt
   ```
2. Set your API key in a `.env` file:
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

## Run the app
```bash
streamlit run app.py
```
