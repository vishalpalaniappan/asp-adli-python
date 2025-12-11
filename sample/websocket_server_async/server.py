#!/usr/bin/env python

import asyncio
from websockets.asyncio.server import serve

async def receieve_message(websocket):
    async for message in websocket:
        print(f"\nReceived message: {message}")
        
async def main():
    async with serve(receieve_message, host="localhost", port=8080) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())