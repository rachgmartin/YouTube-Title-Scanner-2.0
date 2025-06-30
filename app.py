
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from scan_titles_weighted_contextual_v3_riskaware import scan_titles_weighted
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

st.set_page_config(page_title="YouTube Title Scanner", layout="centered")

# -- Custom dark theme styling --
st.markdown(
    """
    <style>
        .stApp {
            background-color: #0e1117;
            color: #e0e0e0;
        }
        .stDataFrame, .stTable {
            background-color: #0e1117;
            color: #e0e0e0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("YouTube Title Scanner")
st.markdown(
    "Scan a YouTube channel for advertiser-unfriendly words and suggest safer alternatives."
)

api_key = st.text_input(
    "Enter your YouTube Data API Key",
    value=os.getenv("YOUTUBE_API_KEY", ""),
    type="password",
)
channel_id = st.text_input("Enter the YouTube Channel ID (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)")
max_results = st.number_input("Maximum number of titles to fetch", min_value=1, max_value=500, value=100)

def get_uploads_playlist_id(api_key, channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
    response = requests.get(url).json()
    try:
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except (KeyError, IndexError):
        return None

def fetch_video_titles(api_key, uploads_playlist_id, max_results):
    titles = []
    page_token = ""
    while len(titles) < max_results:
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?key={api_key}&playlistId={uploads_playlist_id}&part=snippet&maxResults=50&pageToken={page_token}"
        response = requests.get(url).json()
        for item in response.get("items", []):
            titles.append(item["snippet"]["title"])
        page_token = response.get("nextPageToken", "")
        if not page_token:
            break
    return titles[:max_results]

if st.button("Scan Titles") and api_key and channel_id:
    try:
        st.info("Fetching video titles...")
        uploads_playlist_id = get_uploads_playlist_id(api_key, channel_id)
        if not uploads_playlist_id:
            st.error("Failed to retrieve uploads playlist. Check Channel ID.")
        else:
            titles = fetch_video_titles(api_key, uploads_playlist_id, max_results)
            if not titles:
                st.warning("No titles found or API quota exceeded.")
            else:
                df_keywords = pd.read_csv("updated_keywords_expanded.csv")

                # The CSV already contains a 'keyword' column. Renaming
                # 'Flagged Keyword' blindly would create duplicate column
                # names which causes `DataFrame` objects to appear when
                # accessing `df_keywords['keyword']`. This leads to errors
                # when calling Series string methods.  Preserve a single
                # 'keyword' column instead.
                if "Flagged Keyword" in df_keywords.columns:
                    if "keyword" not in df_keywords.columns:
                        df_keywords.rename(columns={"Flagged Keyword": "keyword"}, inplace=True)
                    else:
                        df_keywords["keyword"] = df_keywords["Flagged Keyword"].fillna(df_keywords["keyword"])
                        df_keywords.drop(columns=["Flagged Keyword"], inplace=True)
                
                df_severity = pd.read_csv("safety_severity_scores.csv", encoding="utf-8-sig")

                # DEBUG: Log original column names
                logger.debug("Raw df_severity.columns = %s", df_severity.columns.tolist())

                # Clean up whitespace and stray characters
                df_severity.columns = df_severity.columns.str.strip().str.replace('"', '').str.replace("'", '')

                # DEBUG: Log cleaned column names
                logger.debug("Cleaned df_severity.columns = %s", df_severity.columns.tolist())

                # Safely rename columns if they exist
                if "Keyword" in df_severity.columns:
                    df_severity.rename(columns={"Keyword": "keyword"}, inplace=True)
                if "SeverityScoreDeduction" in df_severity.columns:
                    df_severity.rename(columns={"SeverityScoreDeduction": "severity"}, inplace=True)

                # Continue with filtering
                df_severity = df_severity[df_severity['keyword'].notna()]
                df_severity['keyword'] = df_severity['keyword'].astype(str).str.lower()

                df_results = scan_titles_weighted(titles, df_keywords, df_severity)
                # Sort results by Safety Score (ascending)
                df_results = df_results.sort_values(by="Safety Score")

                # Apply color scaling to Safety Score column
                styled_df = df_results.style.background_gradient(
                    cmap="RdYlGn_r", subset=["Safety Score"]
                )

                st.success("Scan complete!")
                st.dataframe(styled_df, use_container_width=True)

                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df_results.to_excel(writer, index=False, sheet_name='Scan Results')
                st.download_button(
                    label="Download Excel File",
                    data=output.getvalue(),
                    file_name="youtube_title_scan_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    except Exception as e:
        st.error(f"Something went wrong: {e}")
