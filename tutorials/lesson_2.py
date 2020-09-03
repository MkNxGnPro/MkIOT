"""
Hello, How are you? Good I hope, it's nice of you to come back.
~Mark

MkIOT - IMP Server and Client

These tutorials are to help you grasp MkIOT.

There are endless things you can create with programming, let MkIOT help you build it faster and more secure.

"""

import time, colorama # For later use

# Let's start off with getting our IP Address

from MkIOT import Get_Device_IPS

DEVICE_IP = Get_Device_IPS()['ext'][0]
print(DEVICE_IP)

# Now let's import the IMP Server
# IMP stands for Instant Message Protocol by MkNxGn

from MkIOT.imp import iot_server

# We will set up the IMP Server

server = iot_server.IOT_Server()
server.HOST = DEVICE_IP
server.PORT = 5000
#server.password = "some_password"       # optionally add a password to the connection - MD5 nonce encryption is used

# We need functions for when we receive different types of data. The type you use will depend on what you're getting done.
# The four types MkIOT has split are: data (for general data), question (data that requires responses), audio, video and ping (this is only for checking if a connection is alive)


# We'll set up data, and questions, not all data types need to be used or have a function defined.
# We will build functions that accept a message param


# When receiving data on either the client or server side, you'll get a message object
# Message objects hold a lot of information on the data being sent across such as:
# messaging.message.connector      # Who sent you the message
# messaging.message.data           # Data that came with the message
# messaging.message.status         # The status of the message ("pending", "sending", "sent", "received")
# messaging.message.timing         # The timing of the message - when it was sent (message.timing.sent), when it was received (message.timing.received) and how long it took to send and get a received reply (message.timing.round_trip)
# and much more

def Data_function(message=iot_server.messaging.message):          # message=iot_server.messaging.message if put here for auto complete
    print("We received a data message:", message.data, "from:", message.connector)

def Question_function(message=iot_server.messaging.message):      # message=iot_server.messaging.message if put here for auto complete
    print(f"{colorama.Fore.CYAN}[ SERVER ] - We received a question from:", message.connector)
    print(f"{colorama.Fore.CYAN}[ SERVER ] - They ask:", colorama.Fore.GREEN, message.data, colorama.Fore.RESET)                        # the data from a question

    reply = input(f"{colorama.Fore.CYAN}[ SERVER ] - Response (type here): {colorama.Fore.RESET}")

    message.answer(reply)                                   # How to respond to a question
                                                            # - Note: not responding to a question will throw an exception (timeout error) for the questioner

def New_Connection(device=iot_server.__IOT_Device__):
    # We receive a IOT_Device on a new connection,
    # This object instance is very much similar to MkIOT.imp.iot_device.IOT_Device() when it comes to functionallity with minor changes in background functions

    # We'll send them a hello
    print(f"{colorama.Fore.CYAN}[ SERVER ] - New Connection:", device.ip)
    print(f"{colorama.Fore.CYAN}[ SERVER ] - Let's say hello", colorama.Fore.RESET)
    device.send_data("hello!")

    
# We not need to link our custom functions to the server

server.on_question       = Question_function   # when we receive a question
server.on_data           = Data_function       # when we receive data
server.on_new_connection = New_Connection      # when a new connection is established
                                               #  - Note: You can change functions to other functions while the server is running or turn them off by turning them to None
 

# That's it! Easy. Now let's start the server!

server.run_server()


# You can optionally run a loop after turning the server on:
# server.run_loop()



# ------------------------------------------------------------------------------------------------------ |
# CLIENT


# Let's build a client to connect to the server

from MkIOT.imp import iot_device


server_connection = iot_device.IOT_Device()
server_connection.HOST = DEVICE_IP                  # Connection details to connect to the host server
server_connection.PORT = 5000
#server_connection.password = "some_password"       # optionally add a password to the connection - MD5 nonce encryption is used


# Like the server, we need to link functions to the connection since data can go both ways


def Client_Data_function(message=iot_server.messaging.message):          # message=iot_server.messaging.message if put here for auto complete
    print(f"{colorama.Fore.GREEN}[ CLIENT ] - We received a data message from:", message.connector, "\n[ CLIENT ] - Message Data:",colorama.Fore.CYAN, message.data, colorama.Fore.RESET)


server_connection.on_data = Client_Data_function


# That's it, we can now connect!
server_connection.connect()

time.sleep(2)

# Let's ask the server a question
question = input("\nWhat should we ask the server? (type here): ")



print("")
while server_connection.connected:    # While we're connected, we'll try to ask the server the question until it completes correctly
    try:
        message = server_connection.ask(question, timeout=30) # Send the server the question with a 30 second timeout
        break
    except:
        print("The server didn't respond fast enough or the connection was closed")
        # Try again

print("\nThe Server Responded:".ljust(30), f"{colorama.Fore.CYAN}{message.response}{colorama.Fore.RESET}")   # To get the response for a question asked, use message.response

print("\nThe Question Timing:", "\nSent Time:".ljust(30), message.timing.sent, "\nReceived and Responded:".ljust(30), message.timing.received, "\nRound Trip:".ljust(30), round(message.timing.round_trip, 1), "Seconds")

"""
Example Output:

    >>> 192.168.0.3
    >>> [ SERVER ] - New Connection: 192.168.0.3
    >>> [ SERVER ] - Let's say hello 
    >>> [ CLIENT ] - We received a data message from: <MkIOT IMP Server Connection: 192.168.0.3>
    >>> [ CLIENT ] - Message Data:  hello! 
    >>> 
    >>> What should we ask the server? (type here): what's your name?
    >>> 
    >>> [ SERVER ] - We received a question from: <MkIOT IMP Client Connection: 192.168.0.3>
    >>> [ SERVER ] - They ask:  what's your name? 
    >>> [ SERVER ] - Response (type here): Dell PowerEdge r710
    >>> 
    >>> The Server Responded:         Dell PowerEdge r710
    >>> 
    >>> The Question Timing:
    >>> Sent Time:                    1599118043.403757
    >>> Received and Responded:       1599118054.586911
    >>> Round Trip:                   11.2 Seconds   (It took me to long to type....)
"""