from essentials.network_ops import Get_GW, Get_IP
from essentials import GetPublicIP
from essentials.network_ops import IP_to_MAC, Get_IP_with_MAC


Get_Device_IPS = Get_IP
Device_IP_to_MAC = IP_to_MAC
Get_Gateway = Get_GW

def ignore(*args):
    pass