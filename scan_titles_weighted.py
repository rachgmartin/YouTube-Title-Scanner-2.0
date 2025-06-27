import pandas as pd

def scan_titles_weighted(titles, df_keywords, df_severity):
    profanity_keywords = ["damn", "hell", "shit", "fuck", "bitch"]
    inappropriate_phrases = ["fired", "cheat", "expose", "kicked out", "problem child"]
    overcoming_tropes = ["can finally walk", "miracle", "defies the odds", "beats the disease", "overcomes"]

    identity_flags = {
        "disability": ["paralyzed", "blind", "deaf", "disabled", "wheelchair", "crippled"],
        "poverty": ["homeless", "poor", "poorest", "broke", "jobless"],
        "mental_health": ["autistic", "depressed", "bipolar", "schizo", "adhd"],
        "race_ethnicity": ["immigrant", "illegal", "foreign", "mexican", "black", "asian"],
        "body_image": ["fat", "obese", "anorexic", "skinny", "ugly"],
        "sexual_identity": ["gay", "lesbian", "trans", "nonbinary", "queer"],
    }

    severity_weights = {
        "profanity": 25,
        "inappropriate": 20,
        "disability": 15,
        "poverty": 10,
        "mental_health": 15,
        "race_ethnicity": 20,
        "body_image": 15,
        "sexual_identity": 20,
        "inspiration_porn": 15,
        "combo": 15,
        "all_caps": 10
    }

    results = []

    for title in titles:
        score = 0
        flagged_terms = []
        tone_flags = []

        title_lower = title.lower()

        # Profanity
        for word in profanity_keywords:
            if word in title_lower:
                score += severity_weights["profanity"]
                flagged_terms.append(word)

        # Inappropriate
        for phrase in inappropriate_phrases:
            if phrase in title_lower:
                score += severity_weights["inappropriate"]
                flagged_terms.append(phrase)

        # Inspiration tropes
        for trope in overcoming_tropes:
            if trope in title_lower:
                score += severity_weights["inspiration_porn"]
                tone_flags.append(f"trope: {trope}")

        # Phrase combo
        if "paralyzed" in title_lower and "walk" in title_lower:
            score += severity_weights["combo"]
            tone_flags.append("combo: paralyzed+walk")

        # All caps
        if title.isupper():
            score += severity_weights["all_caps"]
            flagged_terms.append("ALL CAPS")

        # Identity-based flags
        for category, keywords in identity_flags.items():
            for word in keywords:
                if word in title_lower:
                    score += severity_weights.get(category, 10)
                    tone_flags.append(f"{category}: {word}")

        # Severity Level
        if score >= 70:
            severity = "High"
        elif score >= 40:
            severity = "Moderate"
        elif score > 0:
            severity = "Low"
        else:
            severity = "None"

        results.append({
            "Title": title,
            "Confidence Score": min(score, 100),
            "Flagged Reasons": ", ".join(flagged_terms) if flagged_terms else "None",
            "Insensitive Tone Flag": ", ".join(tone_flags) if tone_flags else "None",
            "Severity": severity
        })

    return pd.DataFrame(results)
