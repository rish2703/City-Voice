from preprocessing import preprocess_text

def classify_complaint(text):
    clean = preprocess_text(text)

    # Simple keyword-based logic (temporary until we add APIs)
    if any(word in clean for word in ["garbage", "waste", "trash", "dustbin"]):
        category = "Waste"
    elif any(word in clean for word in ["water", "leakage", "pipe"]):
        category = "Water"
    elif any(word in clean for word in ["traffic", "congestion", "signal", "jam"]):
        category = "Traffic"
    elif any(word in clean for word in ["electricity", "power", "light", "voltage"]):
        category = "Electricity"
    elif any(word in clean for word in ["sewage", "drainage", "sanitation"]):
        category = "Sanitation"
    elif any(word in clean for word in ["noise", "loud", "sound"]):
        category = "Noise"
    else:
        category = "Other"

    return category
