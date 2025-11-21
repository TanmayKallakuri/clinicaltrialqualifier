# test_claude_api.py

from anthropic import Anthropic
import os

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("✗ Error: ANTHROPIC_API_KEY not set")
    print("\nRun this first:")
    print('  $env:ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"')
    exit(1)

print(f"✓ API Key found: {api_key[:20]}...")

# Test connection
try:
    client = Anthropic(api_key=api_key)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": "Say 'API test successful' if you can read this."
        }]
    )
    
    response = message.content[0].text
    
    print("\n" + "="*50)
    print("CLAUDE API TEST")
    print("="*50)
    print(f"\nClaude's response: {response}")
    print(f"\nTokens used: {message.usage.input_tokens + message.usage.output_tokens}")
    print(f"Model: {message.model}")
    
    print("\n✓ API key is working!")
    print("="*50)
    
except Exception as e:
    print(f"\n✗ API test failed: {e}")
    print("\nPossible issues:")
    print("1. Invalid API key")
    print("2. No credits remaining")
    print("3. Network connection issue")