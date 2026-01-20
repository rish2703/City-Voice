from ai.priority import assign_priority_fallback

test_cases = [
    ("Traffic - High", "Multiple potholes on Main Street are causing accidents. Three cars damaged today. Major safety hazard."),
    ("Water - High", "Water pipe burst in downtown area. No water supply for 500 households. Urgent!"),
    ("Electricity - High", "Power outage affecting entire North district. Hospital running on backup power. Critical situation!"),
    ("Sanitation - High", "Garbage overflowing for 5 days. Foul smell spreading disease. Immediate cleanup needed!"),
    ("Traffic - Medium", "Small cracks appearing on Oak Street. No accidents yet but needs repair soon."),
    ("Water - Medium", "Slight water leakage from municipal line in residential area. Regular water supply maintained."),
    ("Electricity - Medium", "Street light not working on Elm Street. Some visibility issues at night."),
    ("Sanitation - Medium", "Minor litter accumulation in park. Need regular cleanup schedule."),
]

print("=" * 80)
print("COMPREHENSIVE PRIORITY CLASSIFICATION TEST")
print("=" * 80)

for category, text in test_cases:
    assigned = assign_priority_fallback(text)
    priority_map = {"P0": "High", "P1": "High", "P2": "Medium", "P3": "Low"}
    display_priority = priority_map.get(assigned, "Unknown")
    
    # Determine if expected
    expected = "High" if "High" in category else "Medium"
    status = "✓" if display_priority == expected else "✗"
    
    print(f"\n{status} {category}")
    print(f"   Text: {text[:70]}...")
    print(f"   AI Priority: {assigned} → {display_priority}")

print("\n" + "=" * 80)
