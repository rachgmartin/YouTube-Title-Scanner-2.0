
import pandas as pd
import re
from context_flags import detect_contextual_flags

def scan_titles_weighted(titles, df_keywords, df_severity):
    print("DEBUG: Columns in df_severity =", df_severity.columns.tolist())
    results = []

    # Risky phrase categories and severity impact
    risky_phrases = {
        "Clickbait": {
            "patterns": [r"you won't believe", r"shocking", r"gone wrong", r"insane", r"crazy", r"exposed"],
            "severity": 10
        },
        "Health Misinformation": {
            "patterns": [r"cure cancer", r"anti-vax", r"miracle cure", r"flat earth"],
            "severity": 30
        },
        "Financial Misleading": {
            "patterns": [r"get rich quick", r"earn \$\d+", r"make money fast", r"no experience needed"],
            "severity": 25
        },
        "Manipulative Urgency": {
            "patterns": [r"limited time", r"before it's too late", r"act now"],
            "severity": 15
        },
        "Overpromising": {
            "patterns": [r"guaranteed results", r"100% success", r"never fail"],
            "severity": 20
        }
    }

    emotional_tones = {
        "Anger": ["hate", "rage", "destroy"],
        "Fear": ["scared", "panic", "terrified"],
        "Drama": ["insane", "unbelievable", "crazy"],
        "Sadness": ["suicide", "depression", "alone", "crying"]
    }

    # Ensure keyword column is lowercase
    df_keywords['keyword'] = df_keywords['keyword'].astype(str).str.lower()

    for title in titles:
        flagged = []
        context_reason = []
        categories = set()
        total_severity = 0

        lower_title = title.lower()

        for row in df_keywords.itertuples(index=False):
            keyword = str(row.keyword).lower()
            if re.search(rf'\b{re.escape(keyword)}\b', lower_title):
                flagged.append(keyword)
                if pd.notna(row.context):
                    context_reason.append(f"{keyword}: {row.context}")
                if pd.notna(row.category):
                    categories.add(row.category)

                severity = df_severity[df_severity['keyword'].astype(str).str.lower() == keyword]['severity'].values
                if severity.size > 0:
                    total_severity += severity[0]

        for label, obj in risky_phrases.items():
            for pattern in obj["patterns"]:
                if re.search(pattern, lower_title):
                    context_reason.append(f"Phrase flagged: {label}")
                    categories.add(label)
                    total_severity += obj["severity"]

        for tone, words in emotional_tones.items():
            for word in words:
                if re.search(rf"\b{re.escape(word)}\b", lower_title):
                    categories.add(f"Emotional Tone: {tone}")

        base_score = 100 - total_severity
        base_score = max(0, min(100, base_score))

        results.append({
            'Title': title,
            'Flagged Words': ", ".join(flagged) if flagged else "None",
            'Context Reason': ", ".join(context_reason) if context_reason else "-",
            'Category': ", ".join(categories) if categories else "-",
            'Safety Score': base_score,
            'Less Harsh Keywords': ", ".join(
                df_keywords[df_keywords['keyword'].isin(flagged)]['Less Harsh Keyword'].fillna("-").astype(str)
            ) if flagged else "-",
            'Alternative Keywords': ", ".join(
                df_keywords[df_keywords['keyword'].isin(flagged)]['Alternative Keyword'].fillna("-").astype(str)
            ) if flagged else "-",
            'Opposite Keywords': ", ".join(
                df_keywords[df_keywords['keyword'].isin(flagged)]['Opposite Keyword'].fillna("-").astype(str)
            ) if flagged else "-"
        })

    return pd.DataFrame(results)
