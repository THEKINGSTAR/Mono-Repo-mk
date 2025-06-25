"""
Test script to verify Anthropic API key is working
"""

import os
import asyncio
import sys

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
        # Import and initialize Anthropic client
        from anthropic import Anthropic
        
        print("🧪 Testing API connection...")
        
        # Initialize client with minimal configuration
        client = Anthropic(
            api_key=api_key,
            timeout=30.0
        )
        
        # Test with a simple message
        print("📤 Sending test message to Claude...")
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with exactly 'API test successful' if you can see this message."
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
            print("   This usually means the API key is valid")
            return True  # Still working, just different response
            
    except ImportError as e:
        print(f"❌ Failed to import Anthropic library: {str(e)}")
        print("   Run: pip install anthropic")
        return False
        
    except Exception as e:
        error_str = str(e).lower()
        print(f"❌ API test failed: {str(e)}")
        
        if "authentication" in error_str or "unauthorized" in error_str:
            print("   This looks like an authentication error.")
            print("   Please check your API key is correct.")
        elif "rate limit" in error_str or "429" in error_str:
            print("   Rate limit reached. API key is valid but you've hit limits.")
            return True
        elif "billing" in error_str or "payment" in error_str:
            print("   Billing issue. Please check your Anthropic account.")
        elif "network" in error_str or "connection" in error_str:
            print("   Network connectivity issue. Check your internet connection.")
        elif "timeout" in error_str:
            print("   Request timed out. This might be a temporary issue.")
        else:
            print("   Unexpected error. Please check your setup.")
        
        return False

async def test_environment():
    """Test environment setup"""
    print("\n🔧 Testing Environment Setup")
    print("=" * 30)
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("   Run: ./scripts/setup_env.sh")
        return False
    
    # Check if python-dotenv is available
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ python-dotenv loaded successfully")
    except ImportError:
        print("⚠️  python-dotenv not found, using os.environ")
    
    # Check required packages
    required_packages = ['anthropic', 'fastapi', 'uvicorn', 'sqlalchemy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🚀 CambioML Backend - Environment Test")
    print("=" * 40)
    
    # Test environment first
    env_ok = await test_environment()
    
    if not env_ok:
        print("\n❌ Environment setup issues found")
        print("   Please fix the issues above before testing API key")
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # Use system environment
    
    # Test API key
    api_success = await test_api_key()
    
    print("\n" + "=" * 40)
    
    if api_success:
        print("🎉 All tests passed! Ready to run the full CambioML system!")
        print("\n🚀 Next steps:")
        print("   1. Run: ./scripts/quick_start.sh")
        print("   2. Or run: docker-compose up --build")
        print("   3. Visit: http://localhost:8000/static/index.html")
    else:
        print("🔧 Please fix the API key issue before proceeding")
        print("\n🔄 Alternative options:")
        print("   1. Run mock demo: python scripts/simple_demo.py")
        print("   2. Check API key at: https://console.anthropic.com/")
        print("   3. Verify account has credits")
        
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
