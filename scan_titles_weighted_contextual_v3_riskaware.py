
import pandas as pd
import re

def scan_titles_weighted(titles, df_keywords, df_severity):
    results = []

    for title in titles:
        flagged = []
        context_reason = []
        categories = set()
        total_severity = 0

        lower_title = title.lower()

        for _, row in df_keywords.iterrows():
            keyword = row['keyword'].lower()
            if re.search(rf'\b{re.escape(keyword)}\b', lower_title):
                flagged.append(keyword)

                if pd.notna(row.get('context')):
                    context_reason.append(row['context'])
                if pd.notna(row.get('category')):
                    categories.add(row['category'])

                severity = df_severity.loc[df_severity['keyword'] == keyword, 'severity'].values
                if severity.size > 0:
                    total_severity += severity[0]

        base_score = 100 - total_severity
        base_score = max(0, min(100, base_score))
        confidence_score = min(100, len(flagged) * 10 + total_severity)

        results.append({
            'Title': title,
            'Flagged Words': ", ".join(flagged) if flagged else "None",
            'Context Reason': ", ".join(context_reason) if context_reason else "-",
            'Category': ", ".join(categories) if categories else "-",
            'Safety Score': base_score,
            'Confidence Score': confidence_score,
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
