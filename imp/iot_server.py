from essentials import socket_ops_v2 as socket_ops
import threading, time
from .. import verification
from . import messaging


class IOT_Server(object):
    
    def __init__(self, HOST=None, PORT=None, on_new_connection=None, password=None, on_data=None, on_question=None, on_video_frame=None, on_audio_frame=None, on_disconnect=None, receive_confirm=True, receive_confirm_timeout=5, challenge_type=verification.types.NONCE, challenge_timeout=5, discovery_server=None):
        self.HOST = HOST
        self.PORT = PORT
        self.password = password
        self.challengeType = challenge_type
        self.on_verified_new_connection_def = on_new_connection # Removing
        self.on_new_connection = on_new_connection              # use this instead
        self.challenge_timeout = challenge_timeout
        self.discovery_server = discovery_server

        self.devices = {}

        self.on_data = on_data
        self.on_question = on_question
        self.on_video_frame = on_video_frame
        self.on_audio_frame = on_audio_frame
        self.on_disconnect = on_disconnect
        self.receive_confirm = receive_confirm
        self.receive_confirm_timeout = receive_confirm_timeout

    def run_server(self, HOST=None, PORT=None, Run_Discovery=True):
        if HOST is not None:
            self.HOST = HOST
        if PORT is not None:
            self.PORT = PORT

        if self.HOST is None or self.PORT is None:
            raise ValueError("HOST and PORT must be set to run a Server")

        self.server = socket_ops.Socket_Server_Host(self.HOST, self.PORT, self.__on_connection__, on_data_recv=None, on_question=None, on_connection_close=self.__lost_connection__, PYTHONIC_only=True)

        if self.discovery_server is not None:
            if self.discovery_server.PORT == self.PORT and self.discovery_server.HOST == self.HOST:
                raise ValueError("Clashing Server PORTS: Cannot have discovery port match Server PORT")
            if self.discovery_server.PORT is None:
                raise ValueError("Discovery port cannot be none")
            self.discovery_server.run()


    def __on_connection__(self, connector=socket_ops.Socket_Server_Client):
        connector.meta['validated'] = False
        identify_message = {"IDENTIFY": ["ip_data"]}
        if self.password != None:
            if self.challengeType == verification.types.NONCE:
                challenge = verification.create_NONCE(self.password)
            connector.meta['challenge'] = challenge
            identify_message['VERIFY'] = challenge['challenge']
            

        response = connector.ask(identify_message)

        if self.password is not None and 'VERIFY' in identify_message:
            try:
                if response['VERIFY'] != challenge['verify']:
                    raise PermissionError("error on verification")
            except:
                connector.send("error on verification")
                connector.shutdown()
                return

        try:
            connector.meta['ip_data'] = response['ip_data']
            try:
                connector.meta['mac'] = response['ip_data']['mac']
            except:
                connector.meta['mac'] = None
        except:
            connector.meta['ip_data'] = None
            connector.meta['mac'] = None

        iot_device = __IOT_Device__(
            self,
            connector,
            connector.meta['mac'],
            on_data=self.on_data,
            on_question=self.on_question,
            on_video_frame=self.on_video_frame,
            on_audio_frame=self.on_audio_frame,
            on_disconnect=self.on_disconnect,
            receive_confirm=self.receive_confirm,
            receive_confirm_timeout=self.receive_confirm_timeout
        )

        connector.meta['validated'] = verification.TimeStamp()

        if connector.meta['mac'] is not None:
            self.devices[connector.meta['mac']] = iot_device
        else:
            self.devices[connector.conID] = iot_device

        if self.on_new_connection is not None:
            threading.Thread(target=self.on_new_connection, args=[iot_device], daemon=True).start()
            
        connector.send("__connect_lock__ disable")    
        
    def __lost_connection__(self, connector):
        if self.on_disconnect is not None:
            threading.Thread(target=self.on_disconnect, args=[self.devices[connector.meta['mac']]], daemon=True).start()
        del self.devices[connector.meta['mac']]
    
    def ping_all(self):
        resp = {}
        for mac in self.devices:
            msg = self.devices[mac].ping()
            resp[mac] = msg.timing.round_trip
        return resp

    def broadcast_data(self, data):
        for mac in self.devices:
            self.devices[mac].send_data(data)

    def shutdown(self):
        self.server.Shutdown()

    def run_loop(self):
        while True:
            time.sleep(4)


class __IOT_Device__(object):

    def __init__(self, server, connector=socket_ops.Socket_Server_Client, mac=None, on_data=None, on_question=None, on_video_frame=None, on_audio_frame=None, on_disconnect=None, receive_confirm=True, receive_confirm_timeout=5, meta=None):
        self.server = server
        
        self.connector = connector
        self.connector.on_question = self.__questions__
        self.connector.on_data = self.__data__
        self.data_usage = self.connector.data_usage

        self.ip, self.port = connector.addr

        self.mac = mac
        self.on_data = on_data
        self.on_question = on_question
        self.on_video_frame = on_video_frame
        self.on_audio_frame = on_audio_frame
        self.on_disconnect = on_disconnect
        self.receive_confirm = receive_confirm
        self.receive_confirm_timeout = receive_confirm_timeout

        self.meta = meta

    def __str__(self):
        return f"<MkIOT IMP Client Connection: {self.ip}>"


    def disconnect(self):
        self.connector.shutdown()

    def send_video_frame(self, frame, wait_till_confirm=False):
        msg = messaging.message(self.connector, frame, self.receive_confirm, self.receive_confirm_timeout, messaging.types.VIDEO, send_as_daemon= not wait_till_confirm)
        return msg

    def send_audio_frame(self, frame, wait_till_confirm=False):
        msg = messaging.message(self.connector, frame, self.receive_confirm, self.receive_confirm_timeout, messaging.types.AUDIO, send_as_daemon= not wait_till_confirm)
        return msg

    def send_data(self, data, wait_till_confirm=False):
        msg = messaging.message(self.connector, data, self.receive_confirm, self.receive_confirm_timeout, messaging.types.DATA, send_as_daemon= not wait_till_confirm)
        return msg

    def ping(self, wait_till_confirm=True):
        msg = messaging.message(self.connector, "PING", self.receive_confirm, self.receive_confirm_timeout, messaging.types.PING, send_as_daemon=not wait_till_confirm)
        return msg

    def ask(self, data, timeout=5):
        msg = messaging.message(self.connector, data, True, timeout, messaging.types.QUESTION)
        return msg

    def __data__(self, data, connector=socket_ops.Socket_Server_Client):
        if connector.meta['validated'] == False and self.password is not None:
            connector.shutdown()
            return

        try:
            connector = self.server.devices[connector.meta['mac']]
        except:
            connector = self.server.devices[connector.conID]
        
        message = messaging.translate_data(data, connector)

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
        connector = question.questioner

        if connector.meta['validated'] == False:
            connector.shutdown()
            return

        data = question.data
        message = messaging.translate_question(question, self)

        if "VIDEO" == message.message_type:
            if self.on_video_frame is not None:
                threading.Thread(target=self.on_video_frame, args=[message], daemon=True).start()
        elif "AUDIO" == message.message_type:
            if self.on_audio_frame is not None:
                threading.Thread(target=self.on_audio_frame, args=[message], daemon=True).start()
        elif "DATA" == message.message_type:
            if self.on_data is not None:
                threading.Thread(target=self.on_data, args=[message], daemon=True).start()
        elif "QUESTION" == message.message_type:
            if self.on_question is not None:
                threading.Thread(target=self.on_question, args=[message], daemon=True).start()
        elif "META_PUSH" == message.message_type:
            connector.meta['meta'] = message.data

