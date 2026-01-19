"""
AI Summary Generator for City Voice

Generates professional summaries of complaints using OpenAI.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(text):
    """
    Generates a professional 1-2 sentence summary of the complaint.
    Also extracts key entities (location, issue type, affected service).
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a municipal complaint summarizer.
Create a professional, concise 1-2 sentence summary of the complaint.
Extract key information: specific location, issue type, and affected service.

Respond in this format:
Summary: [1-2 sentence professional summary]
Location: [specific location mentioned]
Issue: [main issue type]
Service: [affected municipal service]"""
                },
                {
                    "role": "user",
                    "content": f"Summarize this complaint: {text}"
                }
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse response
        lines = content.split('\n')
        summary = ""
        location = ""
        issue = ""
        service = ""
        
        for line in lines:
            if line.startswith("Summary:"):
                summary = line.replace("Summary:", "").strip()
            elif line.startswith("Location:"):
                location = line.replace("Location:", "").strip()
            elif line.startswith("Issue:"):
                issue = line.replace("Issue:", "").strip()
            elif line.startswith("Service:"):
                service = line.replace("Service:", "").strip()
        
        return {
            "summary": summary if summary else text[:100] + "...",
            "entities": {
                "location": location,
                "issue": issue,
                "service": service
            }
        }
            
    except Exception as e:
        print(f"AI summary generation failed: {e}")
        # Fallback to simple truncation
        return {
            "summary": text[:100] + "..." if len(text) > 100 else text,
            "entities": {
                "location": "Not extracted",
                "issue": "Not extracted",
                "service": "Not extracted"
            }
        }


def test_summary_generator():
    """Test the summary generator with sample complaints"""
    test_complaints = [
        "Urgent sewage overflow near ABC School. The drain has been blocked for 3 days and the smell is unbearable. Many students are falling sick.",
        "Streetlight not working on MG Road for the past week. Very dangerous at night.",
        "Garbage collection not happening in Sector 12 for last 4 days. Waste is piling up.",
    ]
    
    print("Testing AI Summary Generator\n" + "=" * 50)
    for i, complaint in enumerate(test_complaints, 1):
        print(f"\nTest {i}:")
        print(f"Original: {complaint}")
        result = generate_summary(complaint)
        print(f"Summary: {result['summary']}")
        print(f"Entities: {result['entities']}")
        print("-" * 50)


if __name__ == "__main__":
    test_summary_generator()
