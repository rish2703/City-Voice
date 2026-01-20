from ai.priority import assign_priority_fallback
from ai.preprocessing import preprocess_text

test_text = "Multiple potholes on Main Street are causing accidents. Three cars damaged today. Major safety hazard."

print("Testing fallback priority assignment:")
print(f"Original: {test_text}\n")

clean = preprocess_text(test_text)
print(f"Cleaned: {clean}\n")

# Check which keywords match
p0_keywords = ["fire", "danger", "life", "death", "emergency", "sparking", "electrical hazard", "major flood"]
p1_keywords = ["outage", "no water", "no power", "leakage", "accident", "hazard", "overflow", "sewage"]
p2_keywords = ["pothole", "trash", "garbage", "repair", "maintenance", "blocked", "smell", "noise"]

print("Keyword Matching:")
p0_matches = [w for w in p0_keywords if w in clean]
p1_matches = [w for w in p1_keywords if w in clean]
p2_matches = [w for w in p2_keywords if w in clean]

if p0_matches:
    print(f"✓ P0 matches: {p0_matches}")
if p1_matches:
    print(f"✓ P1 matches: {p1_matches}")
if p2_matches:
    print(f"✓ P2 matches: {p2_matches}")

print(f"\nAssigned Priority: {assign_priority_fallback(test_text)}")
