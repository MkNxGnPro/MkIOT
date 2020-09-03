from MkIOT.imp import iot_device, messaging
from MkIOT.discovery import broadcast
from MkIOT import Get_Device_IPS
from MkIOT.tools import image

import json, time

import cv2



DEVICE_NAME =      "MK_IOT_SCREEN"               # Change this to anything you want
DEVICE_PASSWORD =  "mkiot"                       # Password for this camera
DEVICE_IP =        Get_Device_IPS()['ext'][0]    # Get This Devices IP
DEVICE_PORT =      7002                          # The Port for audio data to be sent back and forth
DISCOVER_PORT =    7001                          # The Port where Screens's will send connect requests to cameras to discover new cameras
HOTPHRASE =        "mkiot_network_device"        # What the camera will respond to when a connect request is sent out

CURRENT_FRAME =    None                          # For later use



# We need to discover all Cameras on our network, lets setup our broadcaster
broadcaster = broadcast.Discovery_Broadcast(DISCOVER_PORT, HOTPHRASE)
# all setup, now let's broadcast our broadcast message and collect Cameras
all_devices = broadcaster.Collect(timeout=2) # We'll wait a max of 4 seconds before we stop waiting for devices to respond to our message

if len(all_devices.All) == 0:
    print("No Devices Responded.")
    exit()

print("")

Cameras = []
for ip in all_devices.All:           # Go through each device that responded to our message
    device = all_devices.All[ip]
    device_data = json.loads(device.discovery_data)
    print(f"{len(Cameras)} - Found Device at IP: {ip}; Type: {device_data['type']}; Name: {device_data['name']}")
    if device_data['type'] == "camera":
        Cameras.append(device_data)

print("")

connect_to = int(input("Which camera would you like to connect to: "))

camera = Cameras[connect_to]

print(f"Connecting to Device at IP: {camera['ip']}:{camera['port']}; Name: {camera['name']}")



def on_video_frame(message=messaging.message): # When we receive a image frame, we'll get it here
    global CURRENT_FRAME
    CURRENT_FRAME = image.decompress_cv2_image(message.data)
    
def on_question(message=messaging.message):
    if message.data == "speed":
        message.answer(float(input("Camera Asks: Desired Frame Rate in Seconds: ")))
    if message.data == "quality":
        message.answer(float(input("Camera Asks: Desired Quality 1-100 (100 being the best): ")))

cameraConnection = iot_device.IOT_Device()                                 # The connection API to the camera
cameraConnection.on_video_frame = on_video_frame                           # Link our function to the connection
cameraConnection.on_question = on_question                                 # Link our function to the connection
cameraConnection.receive_confirm = False                                   # We don't need confirmation that our frames are being received since we'll be hearing them
cameraConnection.password = DEVICE_PASSWORD                                # camera's password

cameraConnection.connect(camera['ip'], camera['port'])                     # Connect to the camera

cameraConnection.send_data("ready")                                        # Tell the camera we are ready

while True:
    if CURRENT_FRAME is not None:
        cv2.imshow("Video Stream", CURRENT_FRAME)  # Grab the frame and decompress it.
        cv2.waitKey(10)

cameraConnection.disconnect()