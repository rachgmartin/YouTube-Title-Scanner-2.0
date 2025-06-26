
import pandas as pd
import re

def analyze_context(title):
    lowered = title.lower()
    context_flags = []

    if "kill" in lowered and ("how to" in lowered or "tutorial" in lowered):
        context_flags.append(("kill", "Instructional violence"))
    if "sex" in lowered and ("gone wrong" in lowered or "leaked" in lowered):
        context_flags.append(("sex", "Suggestive content"))
    if "drug" in lowered and ("try" in lowered or "challenge" in lowered):
        context_flags.append(("drug", "Recreational drug use"))
    if "dead" in lowered and ("found" in lowered or "body" in lowered):
        context_flags.append(("dead", "Shocking death"))
    if "abuse" in lowered and ("caught" in lowered or "filmed" in lowered):
        context_flags.append(("abuse", "Graphic abuse reference"))

    return context_flags

def scan_titles_weighted(titles, df_mapping, df_severity):
    severity_lookup = dict(zip(df_severity['Keyword'].str.lower(), df_severity['SeverityScoreDeduction']))
    results = []

    for title in titles:
        flagged = []
        lh_list = []
        alt_list = []
        opp_list = []
        score = 100
        context_reasons = []

        for _, row in df_mapping.iterrows():
            word = row['Flagged Keyword']
            if re.search(rf'\b{re.escape(word)}\b', title, re.IGNORECASE):
                flagged.append(word)
                lh_list.append(row['Less Harsh Keyword'])
                alt_list.append(row['Alternative Keyword'])
                opp_list.append(row['Opposite Keyword'])
                score -= severity_lookup.get(word.lower(), 10)

        for word, reason in analyze_context(title):
            if word not in flagged:
                flagged.append(word)
                lh_list.append("-")
                alt_list.append("-")
                opp_list.append("-")
                score -= severity_lookup.get(word.lower(), 10)
            context_reasons.append(f"{word}: {reason}")

        score = max(score, 0)
        results.append({
            "Title": title,
            "Flagged Words": ", ".join(flagged) if flagged else "None",
            "Context Reason": "; ".join(context_reasons) if context_reasons else "-",
            "Safety Score": score,
            "Less Harsh Keywords": ", ".join(lh_list) if lh_list else "-",
            "Alternative Keywords": ", ".join(alt_list) if alt_list else "-",
            "Opposite Keywords": ", ".join(opp_list) if opp_list else "-"
        })

    return pd.DataFrame(results)
