import time
from ai.preprocessing import preprocess_text
from ai.classifier import classify_complaint
from ai.priority import assign_priority_with_reasoning
from ai.ai_summary import generate_summary

def process_complaint(text):
    """
    Complete AI-powered complaint processing pipeline.
    Includes classification, priority assignment, and summary generation.
    """
    start_time = time.time()
    
    # 1. Clean the text
    clean = preprocess_text(text)
    
    # 2. Predict category using AI
    category = classify_complaint(text)
    
    # 3. Predict priority with reasoning using AI
    priority_result = assign_priority_with_reasoning(text)
    priority = priority_result["priority"]
    priority_reasoning = priority_result["reasoning"]
    
    # 4. Generate AI summary
    summary_result = generate_summary(text)
    ai_summary = summary_result["summary"]
    
    # 5. Calculate processing time
    processing_time = time.time() - start_time
    
    # 6. Return structured result
    return {
        "original_text": text,
        "clean_text": clean,
        "category": category,
        "priority": priority,
        "ai_summary": ai_summary,
        "priority_reasoning": priority_reasoning,
        "processing_time": processing_time,
        "is_ai_processed": True
    }
