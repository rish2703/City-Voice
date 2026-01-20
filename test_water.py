from ai.priority import assign_priority_fallback
from ai.preprocessing import preprocess_text

test_text = "Water pipe burst in downtown area. No water supply for 500 households. Urgent!"

print("Testing water complaint priority assignment:")
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
else:
    print("✗ P0 matches: None")
if p1_matches:
    print(f"✓ P1 matches: {p1_matches}")
else:
    print("✗ P1 matches: None")
if p2_matches:
    print(f"✓ P2 matches: {p2_matches}")
else:
    print("✗ P2 matches: None")

assigned = assign_priority_fallback(test_text)
print(f"\nAssigned Priority: {assigned}")

# Expected: P1 (High)
if assigned == "P1":
    print("✓ CORRECT: Should be P1 (High)")
else:
    print(f"✗ ERROR: Got {assigned}, expected P1")
