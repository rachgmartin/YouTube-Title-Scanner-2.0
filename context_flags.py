
import re

def detect_contextual_flags(title):
    title = title.lower()
    context_reasons = []

    # Risky intent phrases
    context_map = {
        "Clickbait": [r"you won't believe", r"shocking", r"insane", r"crazy", r"exposed"],
        "Health Misinformation": [r"cure cancer", r"anti-vax", r"miracle cure", r"flat earth"],
        "Financial Misleading": [r"get rich quick", r"earn \$\d+", r"make money fast", r"no experience needed"],
        "Manipulative Urgency": [r"limited time", r"before it's too late", r"act now"],
        "Overpromising": [r"guaranteed results", r"100% success", r"never fail"]
    }

    for label, patterns in context_map.items():
        for pattern in patterns:
            if re.search(pattern, title):
                context_reasons.append(f"Phrase flagged: {label}")

    return context_reasons
