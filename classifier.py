import os
from openai import OpenAI
from dotenv import load_dotenv
from preprocessing import preprocess_text

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_complaint_ai(text):
    """
    Uses OpenAI GPT-4 to classify the complaint into predefined categories.
    Falls back to keyword-based classification if API fails.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert complaint classifier for municipal services.
Classify the complaint into exactly ONE of these categories:
- Waste (garbage, trash, dustbin, refuse collection)
- Water (leakage, supply, pipe, contamination)
- Traffic (congestion, signal, jam, accident, parking)
- Electricity (power, outage, transformer, wiring)
- Sanitation (sewage, drainage, toilet, cleanliness)
- Noise (loud sounds, construction, disturbance)
- Other (anything that doesn't fit above)

Return ONLY the category name, nothing else."""
                },
                {
                    "role": "user",
                    "content": f"Classify this complaint: {text}"
                }
            ],
            temperature=0.3,  # Lower temperature for consistent classification
            max_tokens=10
        )
        
        category = response.choices[0].message.content.strip()
        
        # Validate category
        valid_categories = ["Waste", "Water", "Traffic", "Electricity", "Sanitation", "Noise", "Other"]
        if category in valid_categories:
            return category
        else:
            print(f"AI returned invalid category '{category}', using fallback")
            return classify_complaint_fallback(text)
            
    except Exception as e:
        print(f"AI classification failed: {e}")
        print("Using fallback keyword-based classification")
        return classify_complaint_fallback(text)


def classify_complaint_fallback(text):
    """
    Fallback keyword-based classification if AI fails.
    """
    clean = preprocess_text(text)

    if any(word in clean for word in ["garbage", "waste", "trash", "dustbin"]):
        return "Waste"
    elif any(word in clean for word in ["water", "leakage", "pipe"]):
        return "Water"
    elif any(word in clean for word in ["traffic", "congestion", "signal", "jam"]):
        return "Traffic"
    elif any(word in clean for word in ["electricity", "power", "light", "voltage"]):
        return "Electricity"
    elif any(word in clean for word in ["sewage", "drainage", "sanitation"]):
        return "Sanitation"
    elif any(word in clean for word in ["noise", "loud", "sound"]):
        return "Noise"
    else:
        return "Other"


def classify_complaint(text):
    """
    Main classification function - uses AI with fallback.
    """
    return classify_complaint_ai(text)
