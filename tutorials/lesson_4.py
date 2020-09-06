"""
Hello, How are you? Good I hope, it's nice of you to come back.
~Mark


MkIOT - Discovery

These tutorials are to help you grasp MkIOT.

There are endless things you can create with programming, let MkIOT help you build it faster and more secure.

"""




# Okay, we have our IP address but what if we wanted to find an IP Address of a different device on the network?
# We will turn to the discovery part of MkIOT.
# Discovery is split into 3 types: Robust (TCP), Fast (UDP) and Broadcast (also UDP (but faster))
# The difference in detail

# Robust Discovery
# Using TCP your device will connect to every IP address (x.x.x.1 - x.x.x.254) on the network one by one (unless you specify multi threading (rippers))
# and wait for the connection to solidify (if that device is active and the port on that device is open).
# Once stable, it will send your hotphrase to that device and wait for a reply for X seconds.
# If the device connects and receives a hotphrase match it will then respond with data you specify.
# 
# It is wise to note, this is the most robust way to transmit data since TCP know's if the device got the message or not
# However, it is the most slow method of the three
# 
# Fast Discovery
# Much like TCP Robust discovery, your device will connect to every IP address (x.x.x.1 - x.x.x.254)
# However, it will not know if the message every received it's destination
# Thus the message sends faster since the connection is not waiting for a solid back and forth connection
# The downside is that you will have to wait X seconds to make sure no one or everyone has responded

# Broadcast Discovery
# This is my preferred method of discovery, it's wicked fast and lightweight
# Unlike Robust and Fast, Broadcast automatically determines your network's UDP broadcast ipaddress,
# It will connect and send user defined hotphrase to the broadcast IP,
# Your router will then forward that message to ALL active hosts on the network.
# All devices running a Discovery server will get the message and respond
# Your device will wait a user defined X seconds for all devices to respond with the user defined data


# For most projects, you'll most likely want to use Broadcast discovery. 




# Let's review the process
"""
    I'll be using the broadcast method in this example.

    In this Example we'll have two devices:

    - Device A (thermometer)
    - Device B (storage computer)

"""

# Both devices
from MkIOT.discovery import broadcast
from MkIOT import Get_IP

DeviceIP = Get_IP()['ext'][0]

"""
    Device B must be configured to run a discovery server to accept incoming discovery.
"""
# Device B

Discovery_Server = broadcast.Discovery_Server(
        DeviceIP,          # HOST - the external IP address you'd like to use
        5001,              # PORT - the port you'd like to use
        "example_3",       # Hotphrase - the connecting device must send this phrase alone to trigger a response
        "Device A"    # Discovery Data - What the hotphrase bearing connectors will get back
    )

# Run the server in the background
Discovery_Server.run()     # You can optionally set the host and port here as well


"""
    Now we can continue with Device A
    Device A collects the tempreture in the room, it needs to send it to the computer for data storage.
   Device A doesn't know what IP Device B is on if DHCP is enabled, it will run a discovery method.
"""

Discovery_Collector = broadcast.Discovery_Broadcast(
        5001,              # PORT - the same port we know Device B has the Discovery Server running on
        "example_3",       # Hotphrase - the phrase to trigger a response
        None               # Broadcast IP - You can specify the IP address you'd like to target with this, MkIOT will get the broadcast IP of the first 'ext' IP on the device otherwise
    )

Discovery_Collector.Collect(
        5,                 # Timeout - How long to wait for responses from all devices - Seconds
        "example_3"        # Hotphrase - Optionally change the phrase to trigger a response
    )

"""
    Device A will send the hotphrase to the router, the router will then distribute this message to all active hosts, Device A will wait for the user defined timeout amount
    Device B will get the hotphrase from the router, however it will have the address of the sender on it.
    Device B will then reply to Device A with it's disovery data defined by the user
    Device A records all replies
"""

# All responses are held in
Discovery_Collector.Devices

# You can get all devices by
Discovery_Collector.Devices.All

# You can get the responses in dictionary format by
Discovery_Collector.Devices.json

"""
FORMAT:
{'192.168.0.xx': "DISCOVERY DATA HERE", '192.168.0.xx': "DISCOVERY DATA HERE", '192.168.0.xx': "DISCOVERY DATA HERE"}
"""

Server_Address = None

# Go through all replies
for IP_ADDRESS in Discovery_Collector.Devices.All:
    # Discovery_Collector.Devices.All[IP_ADDRESS] = an instance of broadcast.Device
    device = Discovery_Collector.Devices.All[IP_ADDRESS]
    print("IP:", device.ip, "; Discovery Response Data:", device.discovery_data)
    if device.discovery_data == "Device A": # When you want a specific device, make it respond with something specific
        Server_Address = device.ip

if Server_Address == None:
    print("Device A was not found")
else:
    print("Device A was found, IP Address:", Server_Address)


"""
Run this program, You should get "Device A was found....

My output:
    >>> [ DDS ] - Device Discovery Scan. Responses: 1
    >>> IP: 192.168.0.3; Discovery Response Data: Device A
    >>> Device A was found, IP Address: 192.168.0.3


Then go back to line 81 and comment it out, rerun the program

You should see "Device A was not found"

My output:
    >>> [ DDS ] - Device Discovery Scan. Responses: 0
    >>> Device A was not found

"""

