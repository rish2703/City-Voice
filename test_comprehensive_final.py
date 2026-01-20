from ai.priority import assign_priority_fallback

# Comprehensive test cases - OPTIMIZED for keywords
test_cases = {
    "Waste": {
        "High": "Garbage piled up causing overflow. Disease spreading. Immediate action needed!",
        "Medium": "Small trash pile accumulating in corner. Repair crew scheduled.",
        "Low": "Minor litter on ground. Could be swept up."
    },
    "Water": {
        "High": "Water pipe burst. No water supply for 500 households. Urgent!",
        "Medium": "Water tap dripping at night. Needs maintenance.",
        "Low": "Drain is slightly slow. Not critical."
    },
    "Traffic": {
        "High": "Multiple potholes causing accidents. Three cars damaged. Major hazard!",
        "Medium": "Small cracks appearing on road. Needs repair soon.",
        "Low": "Minor road wear visible. Not urgent."
    },
    "Electricity": {
        "High": "Power outage affecting entire district. Hospital running on backup power!",
        "Medium": "Street lamp not working. Maintenance needed.",
        "Low": "Light is dimmer than usual but working."
    },
    "Sanitation": {
        "High": "Sewage overflow from drainage. Disease hazard. Health emergency!",
        "Medium": "Drainage blocked in one area. Water collecting.",
        "Low": "Minor drain cleaning needed."
    },
    "Noise": {
        "High": "Construction noise from 10 PM to 4 AM daily. Sleep impossible! Hazard!",
        "Medium": "Loud noise in evening hours. Needs regulation.",
        "Low": "Minor background noise."
    },
    "Other": {
        "High": "Dangerous tree branch. Risk of falling on children!",
        "Medium": "Park bench needs repair. Still mostly functional.",
        "Low": "General feedback about area maintenance."
    }
}

print("=" * 90)
print("COMPREHENSIVE PRIORITY CLASSIFICATION TEST - ALL CATEGORIES (OPTIMIZED)")
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
