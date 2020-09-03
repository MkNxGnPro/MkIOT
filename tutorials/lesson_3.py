"""
Hello, How are you? Good I hope, it's nice of you to come back.
~Mark


MkIOT - Setting up an IMP Client - IOT Device
-- Not built to be ran (Document only)

These tutorials are to help you grasp MkIOT.

There are endless things you can create with programming, let MkIOT help you build it faster and more secure.

"""

# Much like a server, a IOT Device is object based

# First imports
from MkIOT.imp import iot_device

# Next, create a IOT_Device connection

connection = iot_device.IOT_Device()
# SIDE NOTE: MkIOT.imp.iot_device.IOT_Device and MkIOT.imp.iot_server.__IOT_Device__ are extremely similar with slightly different background processes but mostly the same foreground functions and attributes


# You then need to set the basic properties that are required to connect to the server
connection.HOST = "127.0.0.1"       # type in the server's IP address
connection.PORT = 5000              # type in the server's port


# There are multiple options that come along with a connection
connection.reconnect                          # Bool      - Reconnect when connection drops
connection.reconnect_seconds                  # Int       - How long to wait until reconnect is attempted
connection.data_usage                         # Object    - MkNxGn_Essentials.socket_ops.socket_ops_v2.Transfer_Record; Calculates how much data has been transfered while the connection was open
connection.data_usage.received.megabytes      # Int       - How many MB were received from the connection
connection.data_usage.sent.megabytes          # Int       - How many MB were sent through the connection
connection.receive_confirm                    # Bool      - Turn the default for receive confirm for messages
connection.connected                          # Bool      - Check if the connection is active or not

# MkIOT allows a password to be set for Connections, using md5 and nonce encrypting
connection.password                           # String    - A String password to use to verify the server is who they say they are


#Now we connect using
connection.connect()

# Much like the server, the IOT_Device has all the same channel attributes


# A basic message function
def message_function(param1):
    pass

# Using the data channel
# The servers attribute for the channel = our function
connection.on_data = message_function

# Using the audio channel
connection.on_audio_frame = message_function

# Using the video channel
connection.on_video_frame = message_function

# Questions
connection.on_question = message_function


# Sending data
#                       Data      Pause program until the connection has verified that the data was received
connection.send_data("something", False)

# Audio, Video
connection.send_audio_frame([0, 220,0,2020], False)

# Video
connection.send_video_frame(b"dnjbhsjdbshd", False)

# Ask a question
connection.ask("hello?")



# Close the connection
connection.disconnect()


