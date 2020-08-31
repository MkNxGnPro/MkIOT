from MkIOT.imp import iot_server
from MkIOT.discovery import broadcast
from MkIOT import Get_Device_IPS

import json, time

from pyaudio import PyAudio




DEVICE_NAME =      "MK_IOT_SPEAKER"              # Change this to anything you want
DEVICE_PASSWORD =  "mkiot"                       # Password for this speaker
DEVICE_IP =        Get_Device_IPS()['ext'][0]    # Get This Devices IP
DEVICE_PORT =      7000                          # The Port for audio data to be sent back and forth
DISCOVER_PORT =    7001                          # The Port where Mic's will send connect requests to speakers to discover new speakers
HOTPHRASE =        "mkiot_network_device"        # What the speaker will respond to when a connect request is sent out


AUDIO_API =        PyAudio()                     # Init PyAudio
AUDIO_CONFIG =     None                          # For later use
DEVICE_SPEAKER =   None                          # For later use



def on_mic_connect(mic=iot_server.__IOT_Device__):
    global AUDIO_CONFIG, DEVICE_SPEAKER

    print("We've received a verified connection")

    # A Mic Device has connected to this server with the correct password,
    # We'll shutdown the discovery server
    DiscoveryServer.shutdown()

    # and ask the Mic for audio configuration and store it for use
    AUDIO_CONFIG = json.loads(mic.ask("config").response)

    print("Mic's Config:", AUDIO_CONFIG)

    # using the config we received, we'll set up our speaker
    DEVICE_SPEAKER = AUDIO_API.open(
            format=AUDIO_CONFIG['format'],
            channels=AUDIO_CONFIG['channels'],
            rate=AUDIO_CONFIG['rate'],
            frames_per_buffer=AUDIO_CONFIG['chunk'],
            output=True
        )

    # let the Mic know we're ready to receive audio frames
    mic.send_data("ready")
    print("waiting for audio")


def on_audio_frame(message=iot_server.messaging.message, mic=iot_server.__IOT_Device__):
    global DEVICE_SPEAKER

    # We've received an audio frame bundle we've got to grab it
    # message > data
    bundle = message.data

    #  let's play it
    print("Playing bundle")
    for frame in bundle:
        DEVICE_SPEAKER.write(frame)
    
def on_disconnect(speaker):
    global DEVICE_SPEAKER, DiscoveryServer
    print("Mic has disconnected")

    # The Mic disconnected, we should let go of the speakers
    DEVICE_SPEAKER.close()

    # let's turn the discovery server back on!
    DiscoveryServer.run()



BROADCAST_RESPONSE = {
        "ip": DEVICE_IP, 
        "port": DEVICE_PORT,
        "type": "speaker",
        "name": DEVICE_NAME
    }                                            # Condense our data into a small message
# When we get a broadcast message that contains our hotphrase, we'll respond with this data

# Create a discovery server that listens to Broadcast messages sent by Mic's for connect
DiscoveryServer = broadcast.Discovery_Server(DEVICE_IP, DISCOVER_PORT, HOTPHRASE, json.dumps(BROADCAST_RESPONSE))



DeviceServer = iot_server.IOT_Server(DEVICE_IP, DEVICE_PORT)                 # Create a server for heavy audio traffic

DeviceServer.password = DEVICE_PASSWORD                                      # Apply our password to this server
DeviceServer.on_verified_new_connection_def = on_mic_connect                 # When we have a verfied connection; do this function
DeviceServer.on_audio_frame = on_audio_frame                                 # Link this function to our function
DeviceServer.on_disconnect = on_disconnect                                   # Link this function to our function
DeviceServer.discovery_server = DiscoveryServer                              # Apply our custom discovery server to this server
DeviceServer.receive_confirm = False                                         # We wont be sending data that needs confirmation

print("Speaker setup and ready.")
DeviceServer.run_server()
print(f"Listening for broadcast messages with hotphrase: '{HOTPHRASE}' - on port:", DISCOVER_PORT)




DeviceServer.run_loop()