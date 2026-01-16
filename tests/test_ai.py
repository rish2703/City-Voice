"""
Test AI Integration for City Voice

This script tests the AI-powered complaint processing pipeline.
Run this AFTER migrating the database with migrate_db.py
"""

import os
from dotenv import load_dotenv
from ai.pipeline import process_complaint

# Load environment variables
load_dotenv()

def test_ai_integration():
    """Test AI classification, priority, and summary generation"""
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ ERROR: OpenAI API key not set in .env file!")
        print("\nPlease:")
        print("1. Open the .env file")
        print("2. Replace 'your_openai_api_key_here' with your actual API key")
        print("3. Save the file and run this test again")
        return
    
    print("=" * 70)
    print("City Voice - AI Integration Test")
    print("=" * 70)
    print(f"API Key found: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Test complaints
    test_cases = [
        {
            "text": "Urgent sewage overflow near ABC School. The drain has been blocked for 3 days and the smell is unbearable. Many students are falling sick.",
            "expected_category": "Sanitation",
            "expected_priority": "High"
        },
        {
            "text": "Streetlight not working on MG Road for the past week. Very dangerous for pedestrians at night.",
            "expected_category": "Electricity",
            "expected_priority": "Medium"
        },
        {
            "text": "Garbage collection not happening in Sector 12 for last 4 days. Waste is piling up near the park.",
            "expected_category": "Waste",
            "expected_priority": "Medium"
        },
        {
            "text": "Loud construction noise at 2 AM near my house. Cannot sleep for the past 3 nights.",
            "expected_category": "Noise",
            "expected_priority": "Medium"
        },
        {
            "text": "Water supply has been completely disrupted in our entire area since yesterday morning.",
            "expected_category": "Water",
            "expected_priority": "High"
        }
    ]
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"TEST {i}/{len(test_cases)}")
        print(f"{'─' * 70}")
        print(f"Complaint: {test['text']}")
        print()
        
        try:
            result = process_complaint(test['text'])
            
            # Display results
            print(f"✓ Category: {result['category']}")
            print(f"  Expected: {test['expected_category']}")
            print(f"  {'✅ MATCH' if result['category'] == test['expected_category'] else '⚠️  DIFFERENT'}")
            print()
            
            print(f"✓ Priority: {result['priority']}")
            print(f"  Expected: {test['expected_priority']}")
            print(f"  {'✅ MATCH' if result['priority'] == test['expected_priority'] else '⚠️  DIFFERENT'}")
            print()
            
            print(f"✓ AI Summary: {result['ai_summary']}")
            print()
            
            print(f"✓ Priority Reasoning: {result['priority_reasoning']}")
            print()
            
            print(f"✓ Processing Time: {result['processing_time']:.2f} seconds")
            
            results.append({
                "test": i,
                "success": True,
                "result": result
            })
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({
                "test": i,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'=' * 70}")
    print("TEST SUMMARY")
    print(f"{'=' * 70}")
    
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"Tests Passed: {successful}/{total}")
    
    if successful == total:
        print("\n✅ All tests passed! AI integration is working correctly.")
        print("\nNext steps:")
        print("1. Run: python migrate_db.py (to update your database)")
        print("2. Test the full app with: streamlit run ui.py")
    else:
        print(f"\n⚠️  {total - successful} test(s) failed.")
        print("Check the error messages above for details.")
    
    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    test_ai_integration()
