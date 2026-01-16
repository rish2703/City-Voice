import os
import google.generativeai as genai
from dotenv import load_dotenv
from ai.preprocessing import preprocess_text

# Load environment variables
load_dotenv()

# Initialize Gemini client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def assign_priority_ai(text, category=None):
    """
    Uses Google Gemini to analyze complaint urgency and assign priority using P0-P3 scale.
    Returns a dictionary with priority and reasoning.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        
        category_context = f"Category: {category}" if category else ""
        
        prompt = f"""You are a Triage Specialist for a City Complaint system. Analyze the complaint urgency and assign a priority level.

Complaint Text: {text}
{category_context}

Priority Levels:
- P0 (Emergency): Immediate danger to life, sparking wires, or major flooding.
- P1 (High): Major service outage (no water/power) or significant safety hazard.
- P2 (Medium): Standard repair needed, non-dangerous (potholes, trash).
- P3 (Low): Minor cosmetic issues or general feedback.

Respond in this exact format:
Priority: [P0/P1/P2/P3]
Reasoning: [One sentence explaining why]

Complaint: {text}"""
        
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Parse response
        lines = content.split('\n')
        priority = "P2"  # Default to Medium
        reasoning = "AI analysis completed"
        
        for line in lines:
            if line.startswith("Priority:"):
                priority = line.replace("Priority:", "").strip()
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()
        
        # Validate priority
        valid_priorities = ["P0", "P1", "P2", "P3"]
        if priority not in valid_priorities:
            print(f"AI returned invalid priority '{priority}', using fallback")
            priority = assign_priority_fallback(text)
            reasoning = "Fallback keyword-based analysis"
        
        return {
            "priority": priority,
            "reasoning": reasoning
        }
            
    except Exception as e:
        print(f"AI priority assignment failed: {e}")
        print("Using fallback keyword-based priority")
        priority = assign_priority_fallback(text)
        return {
            "priority": priority,
            "reasoning": "Fallback keyword-based analysis"
        }


def assign_priority_fallback(text):
    """
    Fallback keyword-based priority assignment if AI fails (P0-P3 scale).
    """
    clean = preprocess_text(text)

    # P0 Priority (Emergency) - Immediate danger
    p0_keywords = ["fire", "danger", "life", "death", "emergency", "sparking", "electrical hazard", "major flood"]
    if any(word in clean for word in p0_keywords):
        return "P0"

    # P1 Priority (High) - Major service outage or significant safety hazard
    p1_keywords = ["outage", "no water", "no power", "leakage", "accident", "hazard", "overflow", "sewage"]
    if any(word in clean for word in p1_keywords):
        return "P1"

    # P2 Priority (Medium) - Standard repair needed, non-dangerous
    p2_keywords = ["pothole", "trash", "garbage", "repair", "maintenance", "blocked", "smell", "noise"]
    if any(word in clean for word in p2_keywords):
        return "P2"

    # P3 Priority (Low) - Minor cosmetic issues or feedback
    return "P3"


def assign_priority(text):
    """
    Main priority assignment function - uses AI with fallback.
    Returns priority string for backward compatibility.
    """
    result = assign_priority_ai(text)
    return result["priority"]


def assign_priority_with_reasoning(text):
    """
    Returns full priority analysis with reasoning.
    Use this when you need the explanation.
    """
    return assign_priority_ai(text)
