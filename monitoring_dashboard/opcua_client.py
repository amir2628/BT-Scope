# # opcua_client.py

# import asyncio
# from asyncua import Client

# async def read_cnc_status():
#     url = "opc.tcp://localhost:4840"  # Replace with your OPC UA server URL
#     async with Client(url=url) as client:
#         root = client.get_root_node()
#         # Assuming your CNC status nodes are under some specific node
#         cnc104_status = await root.get_child(["0:Objects", "2:CNC104", "2:Status"]).read_value()
#         cnc105_status = await root.get_child(["0:Objects", "2:CNC105", "2:Status"]).read_value()
#         return {"cnc104": cnc104_status, "cnc105": cnc105_status}


# # opcua_client.py

# import asyncio
# from asyncua import Client
# from .mqtt_publisher import publish_status  # Import the publish_status function

# async def read_cnc_status():
#     url = "opc.tcp://localhost:4840"  # Replace with your OPC UA server URL
#     async with Client(url=url) as client:
#         root = client.get_root_node()
#         # Assuming your CNC status nodes are under some specific node
#         cnc104_node = await root.get_child(["0:Objects", "2:CNC104", "2:Status"])
#         cnc105_node = await root.get_child(["0:Objects", "2:CNC105", "2:Status"])

#         while True:
#             cnc104_status = await cnc104_node.read_value()
#             cnc105_status = await cnc105_node.read_value()

#             # Prepare messages for MQTT
#             cnc104_message = {
#                 "id": "104",
#                 "status": bool(cnc104_status),
#                 "time": "",  # Add time if needed
#                 "parts": 0,  # Add parts if needed
#                 "details": "",  # Add details if needed
#                 "percent": 0  # Add percent if needed
#             }

#             cnc105_message = {
#                 "id": "105",
#                 "status": bool(cnc105_status),
#                 "time": "",  # Add time if needed
#                 "parts": 0,  # Add parts if needed
#                 "details": "",  # Add details if needed
#                 "percent": 0  # Add percent if needed
#             }

#             # Publish messages to MQTT topics
#             publish_status("cnc/104/status", cnc104_message)
#             publish_status("cnc/105/status", cnc105_message)

#             await asyncio.sleep(1)  # Adjust as needed for the publishing interval

# if __name__ == "__main__":
#     asyncio.run(read_cnc_status())


# # opcua_client.py

# import asyncio
# import aiohttp
# from asyncua import Client

# async def read_cnc_status():
#     url = "http://localhost:8000/update_cnc_status/"
#     async with Client("opc.tcp://localhost:4840") as client:
#         root = client.get_root_node()
#         # Assuming your CNC status nodes are under some specific node
#         cnc104_status_node = await root.get_child(["0:Objects", "2:CNC104", "2:Status"])
#         cnc104_status = await cnc104_status_node.read_value()
        
#         cnc105_status_node = await root.get_child(["0:Objects", "2:CNC105", "2:Status"])
#         cnc105_status = await cnc105_status_node.read_value()

#         # Prepare data to send to Django view
#         data = {
#             'cnc104_status': "Active" if cnc104_status else "Idle",
#             'cnc104_details': "Details for CNC 104",  # Example details, replace with actual data
#             'cnc104_time': "10:00 AM",  # Example time, replace with actual data
#             'cnc104_percent': 75,  # Example percentage, replace with actual data
#             'cnc104_parts': 50,  # Example parts, replace with actual data
#             'cnc105_status': "Active" if cnc105_status else "Idle",
#             'cnc105_details': "Details for CNC 105",  # Example details, replace with actual data
#             'cnc105_time': "11:00 AM",  # Example time, replace with actual data
#             'cnc105_percent': 85,  # Example percentage, replace with actual data
#             'cnc105_parts': 75,  # Example parts, replace with actual data
#             # Add more variables as needed for additional CNC cards
#         }

#         # Send HTTP POST request to Django view
#         async with aiohttp.ClientSession() as session:
#             async with session.post(url, data=data) as response:
#                 response_text = await response.text()
#                 print(response_text)  # Optional: Print response for debugging


# opcua_client.py

import asyncio
import aiohttp
from asyncua import Client

async def read_cnc_status():
    url = "http://localhost:8000/update_cnc_status/"
    async with Client("opc.tcp://localhost:4840") as client:
        root = client.get_root_node()
        # Assuming your CNC status nodes are under some specific node
        cnc104_status_node = await root.get_child(["0:Objects", "2:CNC104", "2:Status"])
        cnc104_status = await cnc104_status_node.read_value()
        
        cnc105_status_node = await root.get_child(["0:Objects", "2:CNC105", "2:Status"])
        cnc105_status = await cnc105_status_node.read_value()

        # Prepare data to send to Django view
        data = {
            'cnc104_status': "Active" if cnc104_status else "Idle",
            'cnc104_details': "Details for CNC 104",  # Example details, replace with actual data
            'cnc104_time': "10:00 AM",  # Example time, replace with actual data
            'cnc104_percent': str(75),  # Example percentage, replace with actual data
            'cnc104_parts': str(50),  # Example parts, replace with actual data
            'cnc105_status': "Active" if cnc105_status else "Idle",
            'cnc105_details': "Details for CNC 105",  # Example details, replace with actual data
            'cnc105_time': "11:00 AM",  # Example time, replace with actual data
            'cnc105_percent': str(85),  # Example percentage, replace with actual data
            'cnc105_parts': str(75),  # Example parts, replace with actual data
            # Add more variables as needed for additional CNC cards
        }

        # Send HTTP POST request to Django view
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_text = await response.text()
                print(response_text)  # Optional: Print response for debugging

# Function to periodically fetch CNC status
async def fetch_cnc_status():
    while True:
        await read_cnc_status()
        await asyncio.sleep(10)  # Adjust interval as needed

# Entry point to start fetching CNC status
if __name__ == "__main__":
    asyncio.run(fetch_cnc_status())
