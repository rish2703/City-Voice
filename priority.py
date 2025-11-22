from preprocessing import preprocess_text

def assign_priority(text):
    clean = preprocess_text(text)

    # High Priority Conditions
    high_keywords = ["urgent", "danger", "leakage", "accident", "flood", "fire", "hazard"]
    if any(word in clean for word in high_keywords):
        return "High"

    # Medium Priority Conditions
    medium_keywords = ["smell", "blocked", "overflow", "noise", "delay"]
    if any(word in clean for word in medium_keywords):
        return "Medium"

    # Default Priority
    return "Low"
