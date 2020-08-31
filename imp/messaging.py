from essentials import socket_ops_v2 as socket_ops
import threading
from essentials import TimeStamp
#from .iot_device import IOT_Device


class directions(object):
    OUT = "OUT"
    IN = "IN"

class types(object):
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"
    DATA = "DATA"
    PING = "PING"
    META_PUSH = "META_PUSH"
    QUESTION = "QUESTION"
    IDENTIFY = "IDENTIFY"


def get_msg_type(data):
    for item in "VIDEO.AUDIO.DATA.PING.IDENTIFY.QUESTION.META_PUSH".split("."):
        if item in data:
            return item

class Time_Keeper(object):

    def __init__(self):
        self.sent = TimeStamp()
    
    def confirmed(self, rcv_ts):
        self.received = rcv_ts
        self.round_trip = (TimeStamp() - self.sent) * 1000

def translate_question(question, connector):
    msg_type = get_msg_type(question.data)
    msg = message(connector, question.data[msg_type], message_direction=directions.IN, message_type=msg_type, question=question)
    if msg_type != types.QUESTION and msg_type != types.IDENTIFY:
        msg.__mark_recv__()
    return msg

def translate_data(data, connector):
    msg_type = get_msg_type(data)
    msg = message(connector, data[msg_type], message_direction=directions.IN, message_type=msg_type)
    return msg

class message(object):
    # iot_device.IOT_Device
    def __init__(self, connector=None, data=None, recv_confirm=None, recv_timeout=5, message_type=types.DATA, message_direction=directions.OUT, send_as_daemon=True, question=None):
        self.connector = connector
        self.data = data
        self.recv_confirm = recv_confirm
        self.recv_timeout = recv_timeout
        self.message_type = message_type
        self.status = "pending"
        self.sent = False
        self.response = None
        self.error = False
        self.received = False
        self.timing = Time_Keeper()
        self.question = question
        

        if message_direction == directions.OUT:
            if self.message_type == types.QUESTION:
                self.__send__()
            elif recv_confirm == True:
                if send_as_daemon:
                    threading.Thread(target=self.__send__, daemon=True).start()
                else:
                    self.__send__()
            else:
                try:
                    self.connector.send({self.message_type: self.data})
                    self.status = "sent"
                    self.sent = True
                except Exception as x:
                    self.error = x
        else:
            self.status = "accepted"
            self.received = True

    def answer(self, data):
        self.question.answer({"ts": TimeStamp(), "resp": data})

    def __mark_recv__(self):
        self.question.answer({'ts': TimeStamp()})
        

    def __send__(self):
        try:
            self.status = "sending"
            resp = self.connector.ask({self.message_type: self.data}, self.recv_timeout)
            self.timing.confirmed(resp['ts'])
            try:
                self.response = resp['resp']
            except:
                self.response = None
            self.sent = True
            self.status = "received"
            self.received = True
        except Exception as x:
            self.error = x
            self.status = str(x)
