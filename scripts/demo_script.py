"""
Demo script for CambioML Computer Use Agent Backend
Run this to demonstrate the system capabilities
"""

import asyncio
import aiohttp
import json
import websockets
from datetime import datetime

class DemoClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = None
        
    async def run_demo(self):
        """Run complete demo sequence"""
        print("🚀 Starting CambioML Computer Use Agent Demo")
        print("=" * 50)
        
        # 1. Create session
        await self.create_session()
        
        # 2. Test WebSocket connection
        await self.test_websocket()
        
        # 3. Send demo commands
        await self.send_demo_commands()
        
        # 4. Check chat history
        await self.check_history()
        
        # 5. Cleanup
        await self.cleanup_session()
        
        print("\n✅ Demo completed successfully!")
    
    async def create_session(self):
        """Create a new session"""
        print("\n1. Creating new session...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/sessions") as response:
                if response.status == 200:
                    data = await response.json()
                    self.session_id = data["id"]
                    print(f"   ✅ Session created: {self.session_id}")
                    print(f"   📺 VNC URL: {data['vnc_url']}")
                    print(f"   🔌 WebSocket URL: {data['websocket_url']}")
                else:
                    print(f"   ❌ Failed to create session: {response.status}")
                    return False
        return True
    
    async def test_websocket(self):
        """Test WebSocket connection"""
        print("\n2. Testing WebSocket connection...")
        
        ws_url = f"ws://localhost:8000/ws/{self.session_id}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print("   ✅ WebSocket connected")
                
                # Send test message
                test_message = {
                    "content": "Hello, can you take a screenshot?"
                }
                await websocket.send(json.dumps(test_message))
                print("   📤 Sent test message")
                
                # Wait for response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(response)
                    print(f"   📥 Received response: {data['type']}")
                except asyncio.TimeoutError:
                    print("   ⏰ Response timeout (expected for demo)")
                    
        except Exception as e:
            print(f"   ❌ WebSocket error: {e}")
    
    async def send_demo_commands(self):
        """Send demonstration commands"""
        print("\n3. Sending demo commands...")
        
        commands = [
            "Take a screenshot of the current screen",
            "Open a text editor",
            "Type 'Hello from CambioML Computer Use Agent!'",
            "Save the file as demo.txt"
        ]
        
        ws_url = f"ws://localhost:8000/ws/{self.session_id}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                for i, command in enumerate(commands, 1):
                    print(f"   📤 Command {i}: {command}")
                    
                    message = {"content": command}
                    await websocket.send(json.dumps(message))
                    
                    # Wait a bit between commands
                    await asyncio.sleep(2)
                    
        except Exception as e:
            print(f"   ❌ Error sending commands: {e}")
    
    async def check_history(self):
        """Check chat history"""
        print("\n4. Checking chat history...")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/sessions/{self.session_id}/history"
            async with session.get(url) as response:
                if response.status == 200:
                    history = await response.json()
                    print(f"   📚 Found {len(history)} messages in history")
                    
                    for msg in history[-3:]:  # Show last 3 messages
                        timestamp = msg['timestamp'][:19]  # Truncate timestamp
                        print(f"   💬 [{timestamp}] {msg['role']}: {msg['content'][:50]}...")
                else:
                    print(f"   ❌ Failed to get history: {response.status}")
    
    async def cleanup_session(self):
        """Clean up the session"""
        print("\n5. Cleaning up session...")
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/sessions/{self.session_id}"
            async with session.delete(url) as response:
                if response.status == 200:
                    print("   ✅ Session cleaned up successfully")
                else:
                    print(f"   ❌ Failed to cleanup session: {response.status}")

async def main():
    demo = DemoClient()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
