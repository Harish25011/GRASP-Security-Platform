import asyncio
import httpx
import websockets
import json

async def test_live_stream():
    # 1. Start Server Stream / load dataset
    print("Loading dataset via /api/load...")
    async with httpx.AsyncClient() as client:
        res = await client.post("http://localhost:8000/api/load", timeout=120.0)
        print("API Load Response:", res.json())
        
    print("Simulating an attack via /api/attack...")
    async with httpx.AsyncClient() as client:
        res = await client.post("http://localhost:8000/api/attack", json={"attack_type": "ddos"})
        print("API Attack Triggered:", res.json()["attack_type"])
        
    print("Connecting to WebSocket...")
    # 2. Connect to WebSocket
    try:
        async with websockets.connect("ws://localhost:8000/ws/events") as ws:
            print("WebSocket connected!")
            # We already triggered an attack, the agent updates should flow in
            for _ in range(3):
                msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(msg)
                print("Received WS Message Type:", data.get("type"))
            print("Stream verified successfully!")
    except Exception as e:
        print("WebSocket check failed:", e)

if __name__ == "__main__":
    asyncio.run(test_live_stream())
