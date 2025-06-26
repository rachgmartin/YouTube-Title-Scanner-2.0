
import streamlit as st
import pandas as pd
import re
from io import BytesIO
from googleapiclient.discovery import build

# Define flagged keywords and metadata
FLAGGED_WORDS = [
    {"Flagged Keyword": "scam", "Less Harsh": "scheme", "Alternative": "trick", "Severity": 0.9},
    {"Flagged Keyword": "scammed", "Less Harsh": "tricked", "Alternative": "fooled", "Severity": 0.85},
    {"Flagged Keyword": "bullied", "Less Harsh": "teased", "Alternative": "picked on", "Severity": 0.8},
    {"Flagged Keyword": "killed", "Less Harsh": "hurt", "Alternative": "taken down", "Severity": 0.95},
    {"Flagged Keyword": "sex", "Less Harsh": "affair", "Alternative": "intimacy", "Severity": 0.98},
    {"Flagged Keyword": "addicted", "Less Harsh": "dependent", "Alternative": "hooked", "Severity": 0.85},
    {"Flagged Keyword": "forced", "Less Harsh": "pressured", "Alternative": "coerced", "Severity": 0.9},
    {"Flagged Keyword": "toxic", "Less Harsh": "unhealthy", "Alternative": "harmful", "Severity": 0.8},
    {"Flagged Keyword": "revenge", "Less Harsh": "payback", "Alternative": "justice", "Severity": 0.75},
    {"Flagged Keyword": "dumped", "Less Harsh": "rejected", "Alternative": "let go", "Severity": 0.7},
    {"Flagged Keyword": "poor", "Less Harsh": "struggling", "Alternative": "underprivileged", "Severity": 0.6},
    {"Flagged Keyword": "harassed", "Less Harsh": "bothered", "Alternative": "disturbed", "Severity": 0.85},
    {"Flagged Keyword": "hates", "Less Harsh": "dislikes", "Alternative": "resents", "Severity": 0.75},
    {"Flagged Keyword": "shamed", "Less Harsh": "embarrassed", "Alternative": "criticized", "Severity": 0.8},
    {"Flagged Keyword": "steals", "Less Harsh": "takes", "Alternative": "snatches", "Severity": 0.85},
    {"Flagged Keyword": "abuses", "Less Harsh": "mistreats", "Alternative": "harms", "Severity": 0.95},
    {"Flagged Keyword": "tormented", "Less Harsh": "mistreated", "Alternative": "distressed", "Severity": 0.9},
    {"Flagged Keyword": "shunned", "Less Harsh": "ignored", "Alternative": "excluded", "Severity": 0.8},
    {"Flagged Keyword": "alienated", "Less Harsh": "excluded", "Alternative": "isolated", "Severity": 0.8},
    {"Flagged Keyword": "ostracized", "Less Harsh": "left out", "Alternative": "rejected", "Severity": 0.85},
    {"Flagged Keyword": "neglected", "Less Harsh": "overlooked", "Alternative": "ignored", "Severity": 0.8}
]

def get_video_titles(channel_id, api_key, max_results=500):
    youtube = build("youtube", "v3", developerKey=api_key)
    titles = []
    next_page_token = None

    while len(titles) < max_results:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=min(50, max_results - len(titles)),
            order="date",
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response["items"]:
            titles.append(item["snippet"]["title"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return titles

def scan_titles(titles, flagged_list):
    df = pd.DataFrame(titles, columns=["Video Title"])
    flagged_data = []

    for title in df["Video Title"]:
        found_keywords = []
        less_harsh = []
        alternative = []
        score = 100
        for word in flagged_list:
            if re.search(rf"\b{word['Flagged Keyword']}\b", title, re.IGNORECASE):
                found_keywords.append(word['Flagged Keyword'])
                less_harsh.append(word['Less Harsh'])
                alternative.append(word['Alternative'])
                score -= word['Severity'] * 20
        flagged_data.append({
            "Video Title": title,
            "Flagged Words": ", ".join(found_keywords) if found_keywords else "None",
            "Less Harsh Keywords": ", ".join(less_harsh) if less_harsh else "-",
            "Alternative Keywords": ", ".join(alternative) if alternative else "-",
            "Safety Score": max(0, round(score, 1))
        })
    return pd.DataFrame(flagged_data)

st.title("YouTube Video Title Scanner")
st.markdown("Scan a YouTube channel for advertiser-unfriendly words and get safer suggestions.")

api_key = st.text_input("🔑 YouTube Data API Key", type="password")
channel_id = st.text_input("📺 YouTube Channel ID (e.g., UC_x5XG1OV2P6uZZ5FSM9Ttw)")
max_results = st.number_input("How many titles to scan?", min_value=10, max_value=500, value=100, step=10)

if st.button("🚨 Scan Titles") and api_key and channel_id:
    try:
        st.info("Fetching video titles...")
        titles = get_video_titles(channel_id, api_key, int(max_results))
        if not titles:
            st.warning("No titles found.")
        else:
            df_results = scan_titles(titles, FLAGGED_WORDS)
            st.success("Scan complete!")
            st.dataframe(df_results)

            output = BytesIO()
            df_results.to_excel(output, index=False, engine='xlsxwriter')
            st.download_button(
                label="📥 Download Results as Excel",
                data=output.getvalue(),
                file_name="title_scan_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"❌ Error: {e}")
