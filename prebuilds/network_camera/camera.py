from MkIOT.imp import iot_server
from MkIOT.discovery import broadcast
from MkIOT import Get_Device_IPS
from MkIOT.tools import image

import json, time, threading

import cv2




DEVICE_NAME =      "MK_IOT_CAMERA"               # Change this to anything you want
DEVICE_PASSWORD =  "mkiot"                       # Password for this camera
DEVICE_IP =        Get_Device_IPS()['ext'][0]    # Get This Devices IP
DEVICE_PORT =      7002                          # The Port for audio data to be sent back and forth
DISCOVER_PORT =    7001                          # The Port where Mic's will send connect requests to cameras to discover new cameras
HOTPHRASE =        "mkiot_network_device"        # What the camera will respond to when a connect request is sent out


DEVICE_CAMERA =   cv2.VideoCapture(0)


def on_screen_connect(device=iot_server.__IOT_Device__):
    global DEVICE_CAMERA

    print("We've received a verified connection")

    # A Screen Device has connected to this server with the correct password,
    # We'll wait until it tells us it is ready to receive frames.

    
def on_disconnect(camera):
    print("Screen has disconnected")


def on_data(message=iot_server.messaging.message):

    if message.data == "ready":    # the device is ready to recieve a video stream
        threading.Thread(target=send_video_to_device, args=[message.connector], daemon=True).start() # Start a background process to send video frames to the device


def send_video_to_device(device=iot_server.__IOT_Device__):
    camera_Speed = float(device.ask("speed", 10).response)   # Ask the device what frame rate to use
    camera_quality = int(device.ask("quality", 10).response) # Ask the device what quality to use
    while True:
        try:
            device.send_video_frame(image.compress_cv2_image(CURRENT_FRAME, camera_quality))
            time.sleep(camera_Speed)             # Wait X seconds before sending another frame
        except Exception as e:
            print(e)
            # There was en exception while trying to send data, the user might have disconnected
            break
    device.disconnect()
    


BROADCAST_RESPONSE = {
        "ip": DEVICE_IP, 
        "port": DEVICE_PORT,
        "type": "camera",
        "name": DEVICE_NAME
    }                                            # Condense our data into a small message
# When we get a broadcast message that contains our hotphrase, we'll respond with this data

# Create a discovery server that listens to Broadcast messages sent by Mic's for connect
DiscoveryServer = broadcast.Discovery_Server(DEVICE_IP, DISCOVER_PORT, HOTPHRASE, json.dumps(BROADCAST_RESPONSE))



DeviceServer = iot_server.IOT_Server(DEVICE_IP, DEVICE_PORT)                 # Create a server for heavy image traffic

DeviceServer.password = DEVICE_PASSWORD                                      # Apply our password to this server
DeviceServer.on_verified_new_connection_def = on_screen_connect              # When we have a verfied connection; do this function
DeviceServer.on_data = on_data                                               # Link this function to our function
DeviceServer.on_disconnect = on_disconnect                                   # Link this function to our function
DeviceServer.discovery_server = DiscoveryServer                              # Apply our custom discovery server to this server
DeviceServer.receive_confirm = False                                         # We wont be sending data that needs confirmation

print("camera setup and ready.")
DeviceServer.run_server()
print(f"Listening for broadcast messages with hotphrase: '{HOTPHRASE}' - on port:", DISCOVER_PORT)



while True:
    _, CURRENT_FRAME = DEVICE_CAMERA.read()              # Read a frame of the camera, and store it as a global variable
    #                                                      this method allows the camera to be read less if there were more users.
    cv2.waitKey(10)                                      # Refresh after a 10 m-seconds