from pipeline import process_complaint
from db import insert_complaint

def process_and_save(name, location, text):
    result = process_complaint(text)

    insert_complaint(
        name,
        location,
        result["original_text"],
        result["clean_text"],
        result["category"],
        result["priority"]
    )

    print("\nFinal Saved Result:")
    print(result)
