
import pandas as pd
import re

def scan_titles_weighted(titles, df_keywords, df_severity):
    results = []
    for title in titles:
        flagged = []
        context_reason = []
        context_flag = False
        identity_flag = False
        insensitive_flag = False
        total_severity = 0

        lower_title = title.lower()

        for _, row in df_keywords.iterrows():
            keyword = row['keyword'].lower()
            if re.search(rf'\\b{re.escape(keyword)}\\b', lower_title):
                flagged.append(keyword)
                if pd.notna(row.get('context')):
                    context_flag = True
                    context_reason.append(row['context'])
                if row.get('category') == 'identity':
                    identity_flag = True
                if row.get('category') == 'insensitive':
                    insensitive_flag = True

                severity = df_severity.loc[df_severity['keyword'].str.lower() == keyword, 'severity'].values
                if severity.size > 0:
                    total_severity += severity[0]

        base_score = 100 - total_severity
        if context_flag:
            base_score -= 5
        if identity_flag:
            base_score -= 5
        if insensitive_flag:
            base_score -= 5

        base_score = max(0, min(100, base_score))

        results.append({
            'Title': title,
            'Flagged Words': ", ".join(flagged) if flagged else "None",
            'Context Reason': ", ".join(context_reason) if context_reason else "-",
            'Safety Score': base_score,
        })

    return pd.DataFrame(results)
