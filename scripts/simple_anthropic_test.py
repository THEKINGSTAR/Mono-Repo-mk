"""
Simple Anthropic API test without extra dependencies
"""

import os

def test_anthropic_simple():
    """Simple test of Anthropic API"""
    print("🔑 Simple Anthropic API Test")
    print("=" * 30)
    
    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ No API key found in environment")
        return False
    
    print(f"✅ API key found: {api_key[:20]}...")
    
    try:
        # Import anthropic
        import anthropic
        print(f"✅ Anthropic library version: {anthropic.__version__}")
        
        # Create client
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Client created successfully")
        
        # Simple test message
        print("📤 Sending test message...")
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=20,
            messages=[{"role": "user", "content": "Say 'Hello World'"}]
        )
        
        print(f"📥 Response: {response.content[0].text}")
        print("✅ API test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    success = test_anthropic_simple()
    if success:
        print("\n🎉 Ready to run the full system!")
    else:
        print("\n🔧 Please check your API key and try again")
