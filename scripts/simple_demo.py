"""
Simple demo script to test the CambioML Computer Use Agent Backend
This version works without requiring the full backend to be running
"""

import asyncio
import json
from datetime import datetime

class MockDemoClient:
    def __init__(self):
        self.session_id = "demo-session-123"
        
    async def run_demo(self):
        """Run a mock demo sequence"""
        print("🚀 CambioML Computer Use Agent - Mock Demo")
        print("=" * 50)
        
        # 1. Simulate session creation
        await self.simulate_session_creation()
        
        # 2. Simulate WebSocket interaction
        await self.simulate_websocket_interaction()
        
        # 3. Simulate agent commands
        await self.simulate_agent_commands()
        
        # 4. Show architecture overview
        await self.show_architecture()
        
        print("\n✅ Mock demo completed!")
        print("\n🔧 To run the full system:")
        print("   1. Make sure Docker is running")
        print("   2. Add your ANTHROPIC_API_KEY to .env file")
        print("   3. Run: docker-compose up --build")
        print("   4. Visit: http://localhost:8000/static/index.html")
    
    async def simulate_session_creation(self):
        """Simulate session creation"""
        print("\n1. 🏗️  Session Creation")
        print("   📡 POST /sessions")
        
        # Simulate API response
        session_data = {
            "id": self.session_id,
            "status": "active",
            "vnc_url": f"/vnc/{self.session_id}",
            "websocket_url": f"/ws/{self.session_id}",
            "created_at": datetime.now().isoformat()
        }
        
        print(f"   ✅ Session created: {session_data['id']}")
        print(f"   📺 VNC URL: {session_data['vnc_url']}")
        print(f"   🔌 WebSocket URL: {session_data['websocket_url']}")
        
        await asyncio.sleep(1)
    
    async def simulate_websocket_interaction(self):
        """Simulate WebSocket interaction"""
        print("\n2. 🔌 WebSocket Connection")
        print("   🔗 Connecting to ws://localhost:8000/ws/demo-session-123")
        print("   ✅ WebSocket connected")
        
        # Simulate message exchange
        user_message = "Take a screenshot of the desktop"
        print(f"   📤 User: {user_message}")
        
        await asyncio.sleep(1)
        
        agent_responses = [
            "I'll take a screenshot for you.",
            "Capturing the current screen...",
            "Screenshot captured successfully! I can see the desktop with various applications."
        ]
        
        for response in agent_responses:
            print(f"   📥 Agent: {response}")
            await asyncio.sleep(0.5)
    
    async def simulate_agent_commands(self):
        """Simulate various agent commands"""
        print("\n3. 🤖 Agent Command Examples")
        
        commands = [
            {
                "user": "Open a web browser and go to google.com",
                "agent": "Opening web browser... Navigating to google.com... Done!"
            },
            {
                "user": "Create a new text file and write 'Hello World'",
                "agent": "Creating new text file... Writing content... File saved as hello.txt"
            },
            {
                "user": "Take a screenshot and describe what you see",
                "agent": "Screenshot taken. I can see a web browser with Google's homepage loaded."
            }
        ]
        
        for i, cmd in enumerate(commands, 1):
            print(f"\n   Command {i}:")
            print(f"   👤 User: {cmd['user']}")
            await asyncio.sleep(1)
            print(f"   🤖 Agent: {cmd['agent']}")
            await asyncio.sleep(1)
    
    async def show_architecture(self):
        """Show system architecture"""
        print("\n4. 🏗️  System Architecture")
        print("""
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
   │   (HTML/JS)     │◄──►│   Backend       │◄──►│   Database      │
   └─────────────────┘    └─────────────────┘    └─────────────────┘
            │                       │                       │
            │                       │                       │
            ▼                       ▼                       ▼
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │   WebSocket     │    │   Docker        │    │   Redis         │
   │   Streaming     │    │   Containers    │    │   Cache         │
   └─────────────────┘    └─────────────────┘    └─────────────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │   VNC Server    │
                          │   (Remote       │
                          │   Desktop)      │
                          └─────────────────┘
        """)
        
        print("\n   🔧 Key Components:")
        print("   • FastAPI: REST APIs + WebSocket endpoints")
        print("   • Docker: Isolated containers per session")
        print("   • PostgreSQL: Chat history persistence")
        print("   • Redis: Session state caching")
        print("   • VNC: Remote desktop access")
        print("   • WebSocket: Real-time streaming")

async def main():
    demo = MockDemoClient()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
