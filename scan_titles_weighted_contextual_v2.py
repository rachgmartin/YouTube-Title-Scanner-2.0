
import pandas as pd
import re

def analyze_context(title):
    lowered = title.lower()
    context_flags = []

    # Violence / harm
    if "kill" in lowered and ("how to" in lowered or "tutorial" in lowered or "plan" in lowered):
        context_flags.append(("kill", "Instructional violence"))
    if "dead" in lowered and ("found" in lowered or "body" in lowered or "accident" in lowered):
        context_flags.append(("dead", "Shocking death"))
    if "beat" in lowered and ("up" in lowered or "badly" in lowered):
        context_flags.append(("beat", "Graphic violence"))
    if "attack" in lowered and ("caught" in lowered or "footage" in lowered):
        context_flags.append(("attack", "Violent content"))

    # Sexual content
    if "sex" in lowered and ("gone wrong" in lowered or "leaked" in lowered or "secret" in lowered):
        context_flags.append(("sex", "Suggestive or sexual framing"))
    if "nude" in lowered or "naked" in lowered:
        context_flags.append(("nude", "Sexualized imagery"))

    # Drug / dangerous behavior
    if "drug" in lowered and ("try" in lowered or "challenge" in lowered or "for 24 hours" in lowered):
        context_flags.append(("drug", "Encouraging drug use"))
    if "high" in lowered and ("on" in lowered or "smoking" in lowered):
        context_flags.append(("high", "Implied drug use"))
    if "overdose" in lowered or re.search(r"\bod\b", lowered):
        context_flags.append(("overdose", "Drug-related content"))

    # Abuse or mistreatment
    if "abuse" in lowered and ("caught" in lowered or "watch" in lowered or "exposed" in lowered):
        context_flags.append(("abuse", "Graphic abuse framing"))
    if "scammed" in lowered and ("got" in lowered or "was" in lowered):
        context_flags.append(("scammed", "Scam victim framing"))
    if "forced" in lowered and ("to" in lowered):
        context_flags.append(("forced", "Non-consensual or coercive framing"))

    # Bullying and harassment
    if "bullied" in lowered or ("made fun of" in lowered):
        context_flags.append(("bullied", "Bullying framing"))
    if "shamed" in lowered or "exposed" in lowered:
        context_flags.append(("shamed", "Public shaming framing"))

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
