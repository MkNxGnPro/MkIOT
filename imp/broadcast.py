from essentials import socket_ops_v2 as socket_ops
import threading
from essentials import network_ops
from .. import Get_Gateway

class Broadcast_Receiver_Server(object):
    def __init__(self, HOST=None, PORT=None, on_data=None, max_buffer=1024):
        self.HOST = HOST
        self.PORT = PORT
        self.max_buffer=1024
        self.on_data = on_data

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

        self.server = socket_ops.UDP_Server(self.HOST, self.PORT, __ignore__, self.__response__, max_buffer=self.max_buffer)
        self.running = True

    def shutdown(self):
        self.server.shutdown()
        self.running = False

    def __response__(self, data, connector=socket_ops.UDP_Server_Client):
        data = data.decode()
        if self.on_data is not None:
            threading.Thread(target=self.on_data, args=[data, connector], daemon=True).start()

def broadcast_message(message, port, on_response=None, boardcast_ip=None, max_buffer=1024):
    if boardcast_ip == None:
        boardcast_ip = network_ops.Get_All_IP_Stat()['ext'][0]['broadcast']

    connector = socket_ops.UDP_Connector(boardcast_ip, port, on_response, 5, max_buffer=max_buffer)
    try:
        connector.send(message.encode())
    except:
        connector.send(message)