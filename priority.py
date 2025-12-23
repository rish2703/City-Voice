import os
from openai import OpenAI
from dotenv import load_dotenv
from preprocessing import preprocess_text

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def assign_priority_ai(text):
    """
    Uses OpenAI GPT-4 to analyze complaint urgency and assign priority.
    Returns a dictionary with priority and reasoning.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at triaging municipal complaints.
Analyze the urgency and assign a priority level:

HIGH Priority (life-threatening, severe public safety/health risks):
- Fire, electrical hazards, gas leaks
- Major water leaks, sewage overflow affecting many people
- Accidents, structural collapse
- Anything posing immediate danger

MEDIUM Priority (significant inconvenience, localized issues):
- Bad smell, blocked drains
- Noise disturbance, minor leaks
- Delayed services, moderate overflow
- Issues affecting specific area but not dangerous

LOW Priority (minor inconveniences, routine issues):
- General cleanliness complaints
- Non-urgent maintenance
- Minor aesthetic issues

Respond in this exact format:
Priority: [High/Medium/Low]
Reasoning: [One sentence explaining why]"""
                },
                {
                    "role": "user",
                    "content": f"Analyze this complaint: {text}"
                }
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse response
        lines = content.split('\n')
        priority = "Medium"  # Default
        reasoning = "AI analysis completed"
        
        for line in lines:
            if line.startswith("Priority:"):
                priority = line.replace("Priority:", "").strip()
            elif line.startswith("Reasoning:"):
                reasoning = line.replace("Reasoning:", "").strip()
        
        # Validate priority
        if priority not in ["High", "Medium", "Low"]:
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
    Fallback keyword-based priority assignment if AI fails.
    """
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
