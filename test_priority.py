import os
from dotenv import load_dotenv
load_dotenv()

# Check if GEMINI_API_KEY is set
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print('✓ GEMINI_API_KEY is configured')
    print(f'  Key: {api_key[:20]}...')
else:
    print('✗ GEMINI_API_KEY is not set')

# Test the priority classification
print('\n--- Testing Priority Classification ---')
from ai.priority import assign_priority_with_reasoning

test_cases = [
    'There is a fire in my building with sparking wires!',
    'No water supply for 3 days in my area',
    'There is a large pothole on my street',
    'The noise from construction is annoying'
]

for i, text in enumerate(test_cases, 1):
    print(f'\nTest {i}: {text}')
    try:
        result = assign_priority_with_reasoning(text)
        priority = result['priority']
        reasoning = result['reasoning']
        print(f'  Priority: {priority}')
        print(f'  Reasoning: {reasoning}')
    except Exception as e:
        print(f'  Error: {e}')
