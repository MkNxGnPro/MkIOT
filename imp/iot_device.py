from essentials import socket_ops_v2 as socket_ops
from .. import verification
import threading
from . import messaging
from .. import discovery
from essentials import time_events
from essentials.network_ops import Get_IP_with_MAC
import time



class IOT_Device(object):

    def __init__(self, HOST=None, PORT=None, on_connected=None, on_data=None, on_question=None, on_video_frame=None, on_audio_frame=None, on_disconnect=None, receive_confirm=True, receive_confirm_timeout=5, password=None, challengeType=verification.types.NONCE, reconnect=True, meta=None):
        self.HOST = HOST
        self.PORT = PORT
        self.reconnect = reconnect
        self.reconnect_seconds = 15
        self.connected = False
        self.password = password
        self.challengeType = challengeType
        self.verified_on_connection = on_connected
        self.config = socket_ops.Configuration()
        self.config.on_question = self.__questions__
        self.config.on_data_recv = self.__data__
        self.config.on_connection_close = self.__disconnected__
        self.config.server_PYTHONIC_only = True
        self.server = socket_ops.Socket_Connector(self.HOST, self.PORT, self.config)
        self.data_usage = self.server.data_usage
        self.ip_data = Get_IP_with_MAC()['ext'][0]
        self.__connect_lock__ = False

        self.on_data = on_data
        self.on_question = on_question
        self.on_video_frame = on_video_frame
        self.on_audio_frame = on_audio_frame
        self.on_disconnect = on_disconnect
        self.receive_confirm = receive_confirm
        self.receive_confirm_timeout = receive_confirm_timeout

        self.meta = meta

    def push_meta(self):
        msg = messaging.message(self.server, self.meta, self.receive_confirm, self.receive_confirm_timeout, messaging.types.META_PUSH, send_as_daemon=False)
        return msg

    def send_video_frame(self, frame, wait_till_confirm=False):
        msg = messaging.message(self.server, frame, self.receive_confirm, self.receive_confirm_timeout, messaging.types.VIDEO, send_as_daemon= not wait_till_confirm)
        return msg

    def send_audio_frame(self, frame, wait_till_confirm=False):
        msg = messaging.message(self.server, frame, self.receive_confirm, self.receive_confirm_timeout, messaging.types.AUDIO, send_as_daemon= not wait_till_confirm)
        return msg

    def send_data(self, data, wait_till_confirm=False):
        msg = messaging.message(self.server, data, self.receive_confirm, self.receive_confirm_timeout, messaging.types.DATA, send_as_daemon= not wait_till_confirm)
        return msg

    def ask(self, data, timeout=5):
        msg = messaging.message(self.server, data, True, timeout, messaging.types.QUESTION)
        return msg

    def ping(self, wait_till_confirm=True):
        msg = messaging.message(self.server, "PING", self.receive_confirm, self.receive_confirm_timeout, messaging.types.PING, send_as_daemon=not wait_till_confirm)
        return msg

    def __data__(self, data):
        if data == "error on verification":
            self.server.shutdown()
            raise PermissionError("Connecting Server Error: Invalid Credentials")

        if data == "__connect_lock__ disable":
            self.__connect_lock__ = False
            return
        
        message = messaging.translate_data(data, self)

        if "VIDEO" == message.message_type:
            if self.on_video_frame is not None:
                threading.Thread(target=self.on_video_frame, args=[message], daemon=True).start()
        elif "AUDIO" in message.message_type:
            if self.on_audio_frame is not None:
                threading.Thread(target=self.on_audio_frame, args=[message], daemon=True).start()
        elif "DATA" in message.message_type:
            if self.on_data is not None:
                threading.Thread(target=self.on_data, args=[message], daemon=True).start()

    def __questions__(self, question=socket_ops.Socket_Question):
        data = question.data
        message = messaging.translate_question(question, self)
        if 'IDENTIFY' in data:
            response = {"ip_data": self.ip_data, "mac": self.ip_data['mac']}

            if self.password == None and "VERIFY" in data:
                self.server.shutdown()
                # Your device set password to false, but the server asked for a password
                raise PermissionError("Connecting Server Error: Possible Spoof")

            if self.challengeType == verification.types.NONCE and self.password is not None and "VERIFY" in data:
                response["VERIFY"] = verification.solve_NONCE(data['VERIFY'], self.password)
                
            question.answer(response)

        elif "VIDEO" in message.message_type:
            if self.on_video_frame is not None:
                threading.Thread(target=self.on_video_frame, args=[message], daemon=True).start()
        elif "AUDIO" in message.message_type:
            if self.on_audio_frame is not None:
                threading.Thread(target=self.on_audio_frame, args=[message], daemon=True).start()
        elif "DATA" in message.message_type:
            if self.on_data is not None:
                threading.Thread(target=self.on_data, args=[message], daemon=True).start()
        elif "QUESTION" in message.message_type:
            if self.on_question is not None:
                threading.Thread(target=self.on_question, args=[message], daemon=True).start()

    def __disconnected__(self):
        self.connected = False
        if self.reconnect:
            time_events.wait_X_Y_and_do(self.reconnect_seconds, self.connect)
        if self.on_disconnect is not None:
            threading.Thread(target=self.on_disconnect, daemon=True).start()
        
    def connect(self, HOST=None, PORT=None):
        if HOST is not None:
            self.HOST = HOST
        if PORT is not None:
            self.PORT = PORT
        try:
            self.__connect_lock__ = True
            self.server.HOST = self.HOST
            self.server.PORT = self.PORT
            self.server.connect()
            while self.__connect_lock__:
                time.sleep(0.01)
            self.connected = True
        except Exception as e:
            print(e)
            self.__connect_lock__ = False
            if self.reconnect:
                time_events.wait_X_Y_and_do(self.reconnect_seconds, self.connect)
            raise e

    def disconnect(self):
        self.server.shutdown()

