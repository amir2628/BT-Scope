# mqtt_publisher.py

import paho.mqtt.client as mqtt

def publish_status(topic, message):
    client = mqtt.Client()
    client.connect("localhost", 1883)  # Replace with your MQTT broker details
    client.publish(topic, message)
    client.disconnect()


# import time
# import json
# import random
# import paho.mqtt.client as mqtt

# # MQTT broker configuration
# broker_url = "localhost"  # Replace with your MQTT broker URL or IP address
# broker_port = 1883  # Replace with your MQTT broker port

# # Create MQTT client instance
# client = mqtt.Client()

# try:
#     # Connect to MQTT broker
#     client.connect(broker_url, broker_port)

#     # Function to simulate CNC status updates and publish to MQTT
#     def publish_status():
#         try:
#             while True:
#                 # Simulate data for CNC 104
#                 cnc104_data = {
#                     "id": "104",
#                     "status": random.choice([True, False]),  # Simulate Active or Idle status
#                     "time": time.strftime("%I:%M %p"),  # Simulate time
#                     "parts": random.randint(0, 1000),  # Simulate number of parts
#                     "details": "00379: " + str(random.randint(0, 10)) + " parts behind",  # Simulate details
#                     "percent": random.randint(0, 100)  # Simulate percentage
#                 }

#                 # Simulate data for CNC 105
#                 cnc105_data = {
#                     "id": "105",
#                     "status": random.choice([True, False]),  # Simulate Active or Idle status
#                     "time": time.strftime("%I:%M %p"),  # Simulate time
#                     "parts": random.randint(0, 1000),  # Simulate number of parts
#                     "details": "00589: " + str(random.randint(0, 30)) + " parts behind",  # Simulate details
#                     "percent": random.randint(0, 100)  # Simulate percentage
#                 }

#                 # Publish CNC 104 status to MQTT topic
#                 client.publish("cnc/104/status", json.dumps(cnc104_data), qos=1, retain=True)

#                 # Publish CNC 105 status to MQTT topic
#                 client.publish("cnc/105/status", json.dumps(cnc105_data), qos=1, retain=True)

#                 # Wait before sending the next update (simulated delay)
#                 time.sleep(5)  # Adjust delay as needed

#         except KeyboardInterrupt:
#             print("Simulation stopped by user.")
#         finally:
#             client.disconnect()

#     if __name__ == "__main__":
#         # Start simulating CNC status updates
#         publish_status()

# except ConnectionRefusedError as e:
#     print(f"Connection to MQTT broker failed: {e}")
# except Exception as e:
#     print(f"An unexpected error occurred: {e}")
# finally:
#     client.disconnect()

