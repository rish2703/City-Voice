from ai.priority import assign_priority_fallback

# Comprehensive test cases for ALL categories and priority levels
test_cases = {
    "Waste": {
        "High": "Garbage piled up for a week causing overflow. Disease spreading. Immediate action needed!",
        "Medium": "Small trash pile accumulating in corner. Needs cleanup soon.",
        "Low": "Minor litter on ground. Could be swept up."
    },
    "Water": {
        "High": "Water pipe burst in downtown area. No water supply for 500 households. Urgent!",
        "Medium": "Minor water leakage from municipal line. Water still available.",
        "Low": "Tap is dripping slightly at night."
    },
    "Traffic": {
        "High": "Multiple potholes causing accidents. Three cars damaged. Safety hazard!",
        "Medium": "Small cracks appearing on road. Needs repair soon.",
        "Low": "Minor road wear visible. Not urgent."
    },
    "Electricity": {
        "High": "Power outage affecting entire district. Hospital running on backup power!",
        "Medium": "Street light not working. Some visibility issues.",
        "Low": "Light is dimmer than usual but working."
    },
    "Sanitation": {
        "High": "Sewage overflow from drainage. Major health hazard. Foul smell spreading disease!",
        "Medium": "Drainage blocked in one area. Water collecting slightly.",
        "Low": "Minor drainage cleaning needed."
    },
    "Noise": {
        "High": "Loud construction noise from 10 PM to 4 AM daily. Sleep impossible!",
        "Medium": "Occasional loud sounds in evening hours.",
        "Low": "Minor background noise."
    },
    "Other": {
        "High": "Major tree branch hanging over school. Risk of falling on children!",
        "Medium": "Park bench needs repair. Still mostly functional.",
        "Low": "General feedback about area maintenance."
    }
}

print("=" * 90)
print("COMPREHENSIVE PRIORITY CLASSIFICATION TEST - ALL CATEGORIES")
print("=" * 90)

results = {
    "High": {"Total": 0, "Correct": 0},
    "Medium": {"Total": 0, "Correct": 0},
    "Low": {"Total": 0, "Correct": 0}
}

priority_map = {"P0": "High", "P1": "High", "P2": "Medium", "P3": "Low"}

for category, priorities in test_cases.items():
    print(f"\n{'─' * 90}")
    print(f"📁 {category.upper()}")
    print(f"{'─' * 90}")
    
    for expected_priority, text in priorities.items():
        assigned = assign_priority_fallback(text)
        display_priority = priority_map.get(assigned, "Unknown")
        
        is_correct = display_priority == expected_priority
        status = "✓" if is_correct else "✗"
        
        results[expected_priority]["Total"] += 1
        if is_correct:
            results[expected_priority]["Correct"] += 1
        
        print(f"\n{status} [{expected_priority}]")
        print(f"   Text: {text[:75]}...")
        print(f"   Assigned: {assigned} → {display_priority}")

# Summary
print(f"\n\n{'=' * 90}")
print("SUMMARY")
print(f"{'=' * 90}")

total_tests = sum(p["Total"] for p in results.values())
total_correct = sum(p["Correct"] for p in results.values())

for priority in ["High", "Medium", "Low"]:
    correct = results[priority]["Correct"]
    total = results[priority]["Total"]
    percentage = (correct / total * 100) if total > 0 else 0
    status = "✓" if correct == total else "✗"
    print(f"{status} {priority}: {correct}/{total} ({percentage:.0f}%)")

print(f"\nOverall: {total_correct}/{total_tests} ({total_correct/total_tests*100:.0f}%)")
print(f"{'=' * 90}")
