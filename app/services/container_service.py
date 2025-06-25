import docker
import asyncio
from typing import Dict
import random

class ContainerService:
    def __init__(self):
        self.client = docker.from_env()
        
    async def create_container(self) -> Dict[str, str]:
        """Create a new container with VNC server"""
        
        # Generate random VNC port
        vnc_port = random.randint(5900, 6000)
        
        try:
            # Create container based on the anthropic computer use demo
            container = self.client.containers.run(
                "ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo",
                detach=True,
                ports={
                    '5900/tcp': vnc_port,  # VNC port
                    '6080/tcp': vnc_port + 1000,  # noVNC web port
                },
                environment={
                    'DISPLAY': ':1',
                    'VNC_PASSWORD': 'password123'
                },
                volumes={
                    '/tmp/.X11-unix': {'bind': '/tmp/.X11-unix', 'mode': 'rw'}
                }
            )
            
            # Wait for container to be ready
            await asyncio.sleep(5)
            
            return {
                "container_id": container.id,
                "vnc_port": vnc_port,
                "novnc_port": vnc_port + 1000
            }
            
        except Exception as e:
            raise Exception(f"Failed to create container: {str(e)}")
    
    async def stop_container(self, container_id: str):
        """Stop and remove container"""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove()
        except Exception as e:
            print(f"Error stopping container {container_id}: {e}")
    
    async def get_container_status(self, container_id: str) -> str:
        """Get container status"""
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except:
            return "not_found"
