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
    def __init__(self, HOST=None, PORT=None, hotphrase="discovery", discovery_data=False):
        self.HOST = HOST
        self.PORT = PORT
        self.hotphrase = hotphrase
        self.discovery_data = discovery_data

        self.running = False

    def run(self, HOST=None, PORT=None):
        if HOST is not None:
            self.HOST = HOST
        if PORT is not None:
            self.PORT = PORT

        def __ignore__(_):
            pass

        self.server = socket_ops.Socket_Server_Host(HOST, PORT, __ignore__, None, on_question=self.__discovery_response__, PYTHONIC_only=True)

    def __discovery_response__(self, question=socket_ops.Socket_Question):
        if question.data == self.hotphrase:
            question.answer(self.discovery_data)
        question.questioner.shutdown()

class Discovery_Runner(object):

    def __init__(self, port, rippers=5, hotphrase="discovery"):
        self.GW = Get_GW()
        self.IP = Get_IP()
        self.rippers = rippers
        self.hotphrase = hotphrase
        self.timeout = 5
        self.check_port = port
        self.base = ".".join(self.GW.split(".")[:3]) + "."
        self.running = 0
        self.Devices = Devices()

    def Collect(self, timeout=5, rippers=None, hotphrase=None):
        if rippers is not None:
            self.rippers = rippers
        if hotphrase is not None:
            self.hotphrase = hotphrase
        self.Devices = Devices()
        self.counted = 0
        self.timeout = timeout

        runners = rippers

        start = 1
        end = 0
        for i in range(1, runners + 1):
            end = 255//runners*i
            if i == runners:
                end = 255
            
            threading.Thread(target=self.__ripper__, args=[start, end, self.check_port], daemon=True).start()
            self.running += 1
            
            start += (255//runners)

        while self.running > 0:
            print("[ DDS ] - Device Discovery Scan. Addresses Contacted:", self.counted, end="\r")
            time.sleep(0.01)
        print("[ DDS ] - Device Discovery Scan. Addresses Contacted:", self.counted)

        return self.Devices
        

    def __ripper__(self, start, end, port):
        while start <= end:
            try:
                rmIP = self.base + str(start)
                self.counted += 1

                try:
                    def __ingnore__(*args):
                        pass

                    config = socket_ops.Configuration()
                    config.server_PYTHONIC_only = True
                    config.on_connection_close = __ingnore__
                    server = socket_ops.Socket_Connector(rmIP, port, config)
                    server.connect(self.timeout)
                    data = server.ask(self.hotphrase)
                    server.shutdown()
                    self.Devices.All[rmIP] = Device(rmIP, data)
                except:
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