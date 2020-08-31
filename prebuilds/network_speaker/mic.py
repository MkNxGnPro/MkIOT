from MkIOT.imp import iot_device, messaging
from MkIOT.discovery import broadcast
from MkIOT import Get_Device_IPS

import json, time

from pyaudio import PyAudio, paInt16



DEVICE_NAME =      "MK_IOT_MIC"                  # Change this to anything you want
DEVICE_PASSWORD =  "mkiot"                       # Password for this speaker
DEVICE_IP =        Get_Device_IPS()['ext'][0]    # Get This Devices IP
DEVICE_PORT =      7000                          # The Port for audio data to be sent back and forth
DISCOVER_PORT =    7001                          # The Port where Speaker will be expecting a connect request
HOTPHRASE =        "mkiot_network_device"        # What the speaker will respond to when a connect request is sent out


AUDIO_API =        PyAudio()                     # Init PyAudio

# Mic config
CHUNK = 1024
FORMAT = paInt16
CHANNELS = 2
RATE = 44100

DEVICE_MIC = AUDIO_API.open(                     # Setup our mic
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        frames_per_buffer=CHUNK,
        input=True
    )


AUDIO_CONFIG = {
    "chunk": CHUNK,
    "format": paInt16,
    "channels": CHANNELS,
    "rate": RATE,
}                                                 # Store our Mic settings to be shared later





# We need to discover all Speakers on our network, lets setup our broadcaster
broadcaster = broadcast.Discovery_Broadcast(DISCOVER_PORT, HOTPHRASE)
# all setup, now let's broadcast our broadcast message and collect speakers
all_devices = broadcaster.Collect(timeout=2) # We'll wait a max of 4 seconds before we stop waiting for devices to respond to our message

if len(all_devices.All) == 0:
    print("No Devices Responded.")
    exit()

print("")

speakers = []
for ip in all_devices.All:           # Go through each device that responded to our message
    device = all_devices.All[ip]
    device_data = json.loads(device.discovery_data)
    print(f"{len(speakers)} - Found Device at IP: {ip}; Type: {device_data['type']}; Name: {device_data['name']}")
    if device_data['type'] == "speaker":
        speakers.append(device_data)

print("")

connect_to = int(input("Which speaker would you like to connect to: "))

speaker = speakers[connect_to]

print(f"Connecting to Device at IP: {speaker['ip']}:{speaker['port']}; Name: {speaker['name']}")




def on_question(question=messaging.message): # If the device we're connecting to ask's us a question it will come up here.
    
    print("Device asked:", question.data)

    if question.data == "config":            # If the speaker asks for mic config, we'll send it our config
        question.answer(json.dumps(AUDIO_CONFIG))


def on_data(message=messaging.message): # If the device we're connecting to ask's us a question it will come up here.
    global SpeakerReady
    print("Device Sent:", message.data)

    if message.data == "ready":
        SpeakerReady = True


SpeakerConnection = iot_device.IOT_Device()                                 # The connection API to the speaker
SpeakerConnection.on_question = on_question                                 # Link our function to the connection
SpeakerConnection.on_data = on_data                                         # Link our function to the connection
SpeakerConnection.receive_confirm = False                                   # We don't need confirmation that our frames are being received since we'll be hearing them
SpeakerConnection.password = DEVICE_PASSWORD                                # Speaker's password

SpeakerReady = False                                                    # Set a variable for the speaker
SpeakerConnection.connect(speaker['ip'], speaker['port'])                   # Connect to the speaker

while SpeakerReady == False:                                            # Wait until the speaker sends that it's ready
    time.sleep(0.5)

print("Speaker is ready for an audio bundles")

while True:

    input("Press ENTER when you're ready to record a 5 Second Audio Message")

    bundle = []

    for i in range(0, int(RATE / CHUNK * 5)):
        data = DEVICE_MIC.read(CHUNK)        # Read data from the Mic
        bundle.append(data)                  # Append it to the bundle

    time.sleep(3)                            # Give yourself time to hear yourself

    print("Sending", end="\r")
    SpeakerConnection.send_audio_frame(bundle) # Send the audio frame bundle
    print("Sent   ")