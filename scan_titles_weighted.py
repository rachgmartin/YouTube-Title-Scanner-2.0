
import pandas as pd
import re

def scan_titles_weighted(titles, df_mapping, df_severity):
    # Normalize column names to avoid attribute errors when using `.str`
    df_severity = df_severity.rename(columns=lambda c: c.strip().lower())

    if 'severityscorededuction' in df_severity.columns:
        df_severity.rename(columns={'severityscorededuction': 'severity'}, inplace=True)

    if 'keyword' not in df_severity.columns or 'severity' not in df_severity.columns:
        raise ValueError("df_severity must contain 'keyword' and 'severity' columns")

    severity_lookup = dict(
        zip(
            df_severity['keyword'].astype(str).str.lower(),
            df_severity['severity']
        )
    )
    results = []

    for title in titles:
        flagged = []
        lh_list = []
        alt_list = []
        opp_list = []
        score = 100

        for _, row in df_mapping.iterrows():
            word = row['Flagged Keyword']
            if re.search(rf'\b{re.escape(word)}\b', title, re.IGNORECASE):
                flagged.append(word)
                lh_list.append(row['Less Harsh Keyword'])
                alt_list.append(row['Alternative Keyword'])
                opp_list.append(row['Opposite Keyword'])
                score -= severity_lookup.get(word.lower(), 10)

        score = max(score, 0)
        results.append({
            "Title": title,
            "Flagged Words": ", ".join(flagged) if flagged else "None",
            "Safety Score": score,
            "Less Harsh Keywords": ", ".join(lh_list) if lh_list else "-",
            "Alternative Keywords": ", ".join(alt_list) if alt_list else "-",
            "Opposite Keywords": ", ".join(opp_list) if opp_list else "-"
        })

    return pd.DataFrame(results)
