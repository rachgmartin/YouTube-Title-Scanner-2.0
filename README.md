# YouTube Title Scanner App

This app scans video titles from a specified YouTube channel to identify potentially advertiser-unfriendly content based on YouTube's advertiser guidelines. It uses keyword matching, context awareness, and severity scoring to flag and suggest safer alternatives.

## Features
- Fetches video titles via YouTube Data API
- Uses a private configured API key so app visitors do not enter one
- Flags sensitive or inappropriate terms
- Applies context-aware scoring
- Outputs Excel reports
- Includes CSS classes for a duotone image filter
- Provides responsive aspect-ratio helpers (1:1, 4:3, 16:9)
- Built-in dark mode styling

## Streamlit Cloud setup
Add the YouTube Data API key to the app's private Streamlit secrets:

```toml
YOUTUBE_API_KEY = "your_api_key_here"
```

In Streamlit Cloud, open the app, go to **Settings** -> **Secrets**, paste the secret above, and save. The app will use this value automatically and will not ask visitors to enter an API key.

Do not commit a real API key to this repository.

## Local setup
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `env.example` to `.env` and add your API key:
   ```bash
   cp env.example .env
   ```
3. Edit `.env` so it contains your real local key:
   ```bash
   YOUTUBE_API_KEY=your_api_key_here
   ```

The app reads Streamlit secrets first, then falls back to environment variables from `.env` for local development.

## Run the app
```bash
streamlit run app.py
```
