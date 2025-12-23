from pipeline import process_complaint
from db import insert_complaint

def process_and_save(name, location, text):
    """
    Process complaint through AI pipeline and save to database.
    Now includes AI summary and priority reasoning.
    """
    result = process_complaint(text)

    insert_complaint(
        name,
        location,
        result["original_text"],
        result["clean_text"],
        result["category"],
        result["priority"],
        ai_summary=result.get("ai_summary"),
        priority_reasoning=result.get("priority_reasoning"),
        is_ai_processed=result.get("is_ai_processed", True)
    )

    print("\n✅ Complaint Processed & Saved:")
    print(f"Category: {result['category']}")
    print(f"Priority: {result['priority']}")
    print(f"AI Summary: {result.get('ai_summary', 'N/A')}")
    print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
    
    return result
