"""
Hello, How are you? Good I hope, it's nice of you to come back.
~Mark


MkIOT - Setting up an IMP Server
    -- Not built to be ran (Document only)

These tutorials are to help you grasp MkIOT.

There are endless things you can create with programming, let MkIOT help you build it faster and more secure.

"""

# Import the IMP Server
# IMP stands for Instant Message Protocol by MkNxGn

from MkIOT.imp import iot_server

# Create an IOT Server Instance
server = iot_server.IOT_Server()

# You then need to set the basic properties that are required to turn the server on
server.HOST = "127.0.0.1"       # We'll use our loopback address
server.PORT = 5000              # We'll use the port 5000

# Those are the only two REQUIRED functions on a server.
# MkIOT allows a password to be set for Connections, using md5 and nonce encrypting
server.password                           # String    - A String password to use to verify the client is who they say they are


# However, even though the server will run there is no linking to the server's receive stream and our program

# We need functions for when we receive different types of data. The type you use will depend on what you're getting done.
# The four types of channels MkIOT has are: data (for general data), question (data that requires responses), audio, and video


# We'll create a basic message function
def message_function(param1):
    pass

# Using the data channel
# The servers attribute for the channel = our function
server.on_data = message_function

# Using the audio channel
server.on_audio_frame = message_function

# Using the video channel
server.on_video_frame = message_function

# Though there are different channels, these channels merly serve as a organizational structure for you.
# I.E, you could send video data on the audio channel, or send audio data on the general data channel
# NOTE - Not all channels need to be pointed to the same functions, they can be pointed to different functions specific for the channel


# The next type and probably most useful is the question channel, a question is a data that get's sent through the network and waits for a response, or an answer to the question
# The data you send could be anything, a word, json dumped dictionary, numbers or anything
# It is the reciving end that must determine what the questioner is asking for and respond to the question.

server.on_question = message_function

# When the connection receives data it is then transformed into a message object : MkIOT.imp.messaging.message
# Message objects hold a lot of information on the data being sent across such as:
# messaging.message.connector      # Who sent you the message
# messaging.message.data           # Data that came with the message
# messaging.message.status         # The status of the message ("pending", "sending", "sent", "received")
# messaging.message.timing         # The timing of the message - when it was sent (message.timing.sent), when it was received (message.timing.received) and how long it took to send and get a received reply (message.timing.round_trip)
# and much more

# The message object is then given to your function as the only parameter

# For linter (auto complete) purposes, creating a channel function like this could be very benificial
from MkIOT.imp import messaging

def on_message(message=messaging.message):
    pass


# There are other functions you can use on your server to get notified about different things
# on_new_connection
# on_disconnect

# on_new_connection and on_disconnect both give a iot_device object : MkIOT.imp.iot_server.__IOT_Device__ to your function as the only parameter

# Example usage
def new_client(client=iot_server.__IOT_Device__):
    print("We have a new client:", client)
    client.send_data("hello!")

server.on_new_connection = new_client


def lost_client(client=iot_server.__IOT_Device__):
    print("We lost client:", client)

server.on_disconnect = lost_client


# These functions can be turned off during program execution by setting them to None
# These functions can be assigned to different functions by setting them to the new functions name




#                                                           About Questions

# NOTE: How to answer a question

def on_question(message=messaging.message):
    print("Question Data:", message.data)       #The data that came with the question message

    # TODO: Do something here; like: check a status, ask a question to something else, get data from the internet. Anything really
    # NOTE: Make sure you do not exceed timeout duration. If timeout duration is exceeded, the program that asked the question will get an exception (timeout error)
    reply = "Beep Beep Boop Boop"

    # TODO: Answer the question

    message.answer(reply)

# NOTE: How to ask a question

# Example usage
def new_client(client=iot_server.__IOT_Device__):
    print("We have a new client:", client)
    #                    question Data   Timeout
    message = client.ask("who are you?", 10)
    
    # when the client responds, you can get the response by
    print(message.response)

