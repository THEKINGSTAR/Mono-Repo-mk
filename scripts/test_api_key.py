"""
Test script to verify Anthropic API key is working
"""

import os
import asyncio
from anthropic import Anthropic

async def test_api_key():
    """Test the Anthropic API key"""
    print("🔑 Testing Anthropic API Key")
    print("=" * 30)
    
    # Load API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        print("   Make sure to set it in your .env file")
        return False
    
    if not api_key.startswith("sk-ant-api03-"):
        print("❌ Invalid API key format")
        print("   API key should start with 'sk-ant-api03-'")
        return False
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    try:
        # Initialize Anthropic client
        client = Anthropic(api_key=api_key)
        
        print("🧪 Testing API connection...")
        
        # Test with a simple message
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with 'API test successful' if you can see this message."
                }
            ]
        )
        
        response_text = message.content[0].text
        print(f"📥 Response: {response_text}")
        
        if "API test successful" in response_text.lower() or "successful" in response_text.lower():
            print("✅ API key is working correctly!")
            return True
        else:
            print("⚠️  API responded but with unexpected content")
            return True  # Still working, just different response
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        
        if "authentication" in str(e).lower():
            print("   This looks like an authentication error.")
            print("   Please check your API key is correct.")
        elif "rate limit" in str(e).lower():
            print("   Rate limit reached. API key is valid but you've hit limits.")
            return True
        elif "billing" in str(e).lower():
            print("   Billing issue. Please check your Anthropic account.")
        
        return False

async def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = await test_api_key()
    
    if success:
        print("\n🎉 Ready to run the full CambioML system!")
        print("   Run: ./scripts/quick_start.sh")
    else:
        print("\n🔧 Please fix the API key issue before proceeding")
        print("   You can still run the mock demo: python scripts/simple_demo.py")

if __name__ == "__main__":
    asyncio.run(main())
