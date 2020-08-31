import netifaces
import socket
import time
import threading
from essentials import socket_ops_v2 as socket_ops
from essentials.network_ops import Get_GW, Get_IP

class Device(object):
    def __init__(self, ip, data):
        self.ip = ip
        self.discovery_data = data
    
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
        

class Discovery_Runner(object):

    def __init__(self, port, runners=5, hotphrase="discovery"):
        self.GW = Get_GW()
        self.IP = Get_IP()
        self.hotphrase = hotphrase
        self.runners = runners
        self.timeout = 5
        self.check_port = port
        self.base = ".".join(self.GW.split(".")[:3]) + "."
        self.running = 0
        self.Devices = Devices()

    def Collect(self, timeout=5, runners=None, hotphrase=None):
        if runners is not None:
            self.runners = runners
        if hotphrase is not None:
            self.hotphrase = hotphrase
        self.Devices = Devices()
        self.counted = 0
        self.timeout = timeout
        self.responses = 0

        runners = self.runners

        start = 1
        end = 0
        for i in range(1, runners + 1):
            end = 255//runners*i
            if i == runners:
                end = 255
            
            threading.Thread(target=self.__runner__, args=[start, end, self.check_port], daemon=True).start()
            self.running += 1
            
            start += (255//runners)

        while self.running > 0:
            print("[ DDS ] - Device Discovery Scan. Addresses Contacted:", self.counted, end="\r")
            time.sleep(0.01)
        print("[ DDS ] - Device Discovery Scan. Addresses Contacted:", self.counted)

        to = 0
        while to < timeout:
            print("[ DDS ] - Device Discovery Scan. Responses:", self.responses, end="\r")
            to += 0.01
            time.sleep(0.01)
        print("[ DDS ] - Device Discovery Scan. Responses:", self.responses)

        return self.Devices

    def __runner_data__(self, data, address):
        self.responses += 1
        self.Devices.All[address[0]] = Device(address[0], data.decode())
        

    def __runner__(self, start, end, port):
        while start <= end:
            try:
                if start == 255:
                    break
                rmIP = self.base + str(start)
                self.counted += 1

                try:
                    connector = socket_ops.UDP_Connector(rmIP, self.check_port, self.__runner_data__, 5)
                    connector.send(self.hotphrase.encode())                    

                except Exception as e:
                    print(e)
                    pass


            except KeyboardInterrupt:
                print("[ UKI ] - User Keyboard Interupt")
                exit()
            except TimeoutError:
                pass
            except Exception as e:
                #print(e)
                pass
            start += 1
        self.running -= 1