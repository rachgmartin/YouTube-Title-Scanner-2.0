
import pandas as pd
import re


def scan_titles_weighted(titles, df_keywords, df_severity):
    import pandas as pd
    import re

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

                # Context and category
                if pd.notna(row.get('context')):
                    context_reason.append(row['context'])
                if pd.notna(row.get('category')):
                    categories.add(row['category'])

                # Severity lookup
                severity = df_severity.loc[df_severity['keyword'] == keyword, 'severity'].values
                if severity.size > 0:
                    total_severity += severity[0]

        # Base safety score
        base_score = 100 - total_severity
        base_score = max(0, min(100, base_score))

        # Confidence: based on number of flagged words and severity
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

                severity = df_severity.loc[df_severity['keyword'] == keyword, 'severity'].values
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
