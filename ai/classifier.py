import os
import google.generativeai as genai
from dotenv import load_dotenv
from ai.preprocessing import preprocess_text

# Load environment variables from .env file
load_dotenv()

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def validate_and_classify_complaint_ai(text, selected_category=None):
    """
    Uses Google Gemini to validate and classify the complaint using triage specialist prompt.
    Returns a structured response with validation, category, priority, and reasoning.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        category_context = f"User-Selected Category: {selected_category}" if selected_category else "No pre-selected category"
        
        prompt = f"""You are a Triage Specialist for a City Complaint system.

User Input: {text}
{category_context}

Task:

1. Validate: Does the text match the category (if provided)? (Yes/No).

2. Classify: Assign the complaint to exactly ONE of these categories:
   - Waste (garbage, trash, dustbin, refuse collection)
   - Water (leakage, supply, pipe, contamination)
   - Traffic (congestion, signal, jam, accident, parking)
   - Electricity (power, outage, transformer, wiring)
   - Sanitation (sewage, drainage, toilet, cleanliness)
   - Noise (loud sounds, construction, disturbance)
   - Other (anything that doesn't fit above)

3. Assign Priority:
   - P0 (Emergency): Immediate danger to life, sparking wires, or major flooding.
   - P1 (High): Major service outage (no water/power) or significant safety hazard.
   - P2 (Medium): Standard repair needed, non-dangerous (potholes, trash).
   - P3 (Low): Minor cosmetic issues or general feedback.

Output Format (EXACTLY as shown):
Validation: [Yes/No]
Category: [category name]
Priority: [P0/P1/P2/P3]
Severity Reason: [1-sentence explanation]"""
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Parse structured response
        result = parse_triage_response(content)
        return result
            
    except Exception as e:
        print(f"AI triage failed: {e}")
        print("Using fallback classification")
        return classify_complaint_fallback(text)


def parse_triage_response(response_text):
    """
    Parse the structured triage response from Gemini.
    """
    result = {
        "validation": "No",
        "category": "Other",
        "priority": "P3",
        "severity_reason": "Unable to determine"
    }
    
    lines = response_text.split('\n')
    for line in lines:
        if line.startswith("Validation:"):
            result["validation"] = line.replace("Validation:", "").strip()
        elif line.startswith("Category:"):
            result["category"] = line.replace("Category:", "").strip()
        elif line.startswith("Priority:"):
            result["priority"] = line.replace("Priority:", "").strip()
        elif line.startswith("Severity Reason:"):
            result["severity_reason"] = line.replace("Severity Reason:", "").strip()
    
    return result


def classify_complaint_ai(text):
    """
    Uses Google Gemini to classify the complaint into predefined categories.
    Falls back to keyword-based classification if API fails.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        
        prompt = """You are an expert complaint classifier for municipal services.
Classify the complaint into exactly ONE of these categories:
- Waste (garbage, trash, dustbin, refuse collection)
- Water (leakage, supply, pipe, contamination)
- Traffic (congestion, signal, jam, accident, parking)
- Electricity (power, outage, transformer, wiring)
- Sanitation (sewage, drainage, toilet, cleanliness)
- Noise (loud sounds, construction, disturbance)
- Other (anything that doesn't fit above)

Return ONLY the category name, nothing else.

Complaint: {text}"""
        
        response = model.generate_content(prompt)
        category = response.text.strip()
        
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
    Uses lowercase original text to avoid stopword removal breaking keywords.
    """
    clean = text.lower()

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
