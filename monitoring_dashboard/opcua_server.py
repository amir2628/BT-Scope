# opcua_server.py

import asyncio
from asyncua import Server

async def simulate_cnc_status():
    while True:
        # Simulate changing status between Idle and Active
        yield False  # Idle
        await asyncio.sleep(7)  # Simulate some delay
        yield True  # Active
        await asyncio.sleep(3)  # Simulate some delay

async def main():
    server = Server()
    await server.init()
    
    # Setup OPC UA namespace
    uri = "http://example.org/CNC"
    idx = await server.register_namespace(uri)
    objects = server.nodes.objects
    
    # Add objects and variables
    cnc_objects = await objects.add_object(idx, "CNC")
    cnc104_status = await cnc_objects.add_variable(idx, "CNC104.Status", False)
    cnc105_status = await cnc_objects.add_variable(idx, "CNC105.Status", False)
    
    # Set up method to simulate status changes
    async def simulate_status(cnc_var, generator):
        async for status in generator:
            await cnc_var.set_value(status)
            await asyncio.sleep(1)
    
    generator1 = simulate_cnc_status()
    generator2 = simulate_cnc_status()
    
    asyncio.create_task(simulate_status(cnc104_status, generator1))
    asyncio.create_task(simulate_status(cnc105_status, generator2))
    
    # Start the server
    await server.start()
    print(f"OPC UA Server started at {server.endpoint}")
    
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
