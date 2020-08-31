import netifaces
import socket
import time
import threading
from essentials import socket_ops_v2 as socket_ops
from essentials.network_ops import Get_GW, Get_IP, Get_All_IP_Stat

class Device(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.discovery_data = data
        self.__new__ = True
    
    @property
    def json(self):
        data = {"ip": self.ip, "discovery_data": self.discovery_data}
        return data 

class Devices(object):
    def __init__(self):
        self.All = {}

    @property
    def json(self):
        data = {}
        for item in self.All:
            data[self.All[item].ip] = self.All[item].json
        return data

class Discovery_Server(object):
    def __init__(self, HOST=None, PORT=None, hotphrase="discovery", discovery_data="Server"):
        self.HOST = HOST
        self.PORT = PORT
        self.hotphrase = hotphrase
        self.discovery_data = discovery_data
        self.responder_function = self.__discovery_response__

        self.running = False

    def run(self, HOST=None, PORT=None):
        if self.running != False:
            return

        if HOST is not None:
            self.HOST = HOST
        if PORT is not None:
            self.PORT = PORT

        def __ignore__(_):
            pass

        self.server = socket_ops.UDP_Server(self.HOST, self.PORT, __ignore__, self.responder_function, max_buffer=len(self.hotphrase))
        self.running = True

    def shutdown(self):
        self.server.shutdown()
        self.running = False

    def __discovery_response__(self, data, connector=socket_ops.UDP_Server_Client):
        data = data.decode()
        if data == self.hotphrase:
            connector.send(self.discovery_data.encode())
        
class Discovery_Broadcast(object):

    def __init__(self, port, hotphrase="discovery"):
        self.GW = Get_GW()
        self.IP = Get_IP()
        self.hotphrase = hotphrase
        self.timeout = 5
        self.check_port = port
        self.base = ".".join(self.GW.split(".")[:3]) + "."
        self.Devices = Devices()

    def Collect(self, timeout=5, hotphrase=None):
        if hotphrase is not None:
            self.hotphrase = hotphrase
        self.Devices = Devices()
        self.timeout = timeout
        self.responses = 0

        connector = socket_ops.UDP_Connector(Get_All_IP_Stat()['ext'][0]['broadcast'], self.check_port, self.__check_in__, 5)
        connector.send(self.hotphrase.encode())

        to = 0
        while to < timeout:
            print("[ DDS ] - Device Discovery Scan. Responses:", self.responses, end="\r")
            to += 0.01
            time.sleep(0.01)

        print("[ DDS ] - Device Discovery Scan. Responses:", self.responses)

        return self.Devices

    def Collect_Yeilder(self):
        to = 0
        while to < timeout:
            print("[ DDS ] - Device Discovery Scan. Responses:", self.responses, end="\r")
            for device in self.Devices.All:
                if self.Devices.All[device].__new__:
                    self.Devices.All[device].__new__ = False
                    yield self.Devices.All[device]
            to += 0.01
            time.sleep(0.01)
        print("[ DDS ] - Device Discovery Scan. Responses:", self.responses)

    def __check_in__(self, data, address):
        self.responses += 1
        self.Devices.All[address[0]] = Device(address[0], data.decode())