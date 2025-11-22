from preprocessing import preprocess_text
from classifier import classify_complaint
from priority import assign_priority

def process_complaint(text):
    # 1. Clean the text
    clean = preprocess_text(text)
    
    # 2. Predict category
    category = classify_complaint(text)
    
    # 3. Predict priority
    priority = assign_priority(text)
    
    # 4. Return structured result
    return {
        "original_text": text,
        "clean_text": clean,
        "category": category,
        "priority": priority
    }
