from essentials.network_ops import Get_GW, Get_IP, IP_to_MAC, Get_IP_with_MAC, Get_All_IP_Stat
from essentials import GetPublicIP

Get_Device_IPS = Get_IP
Get_All_Net_Ifaces = Get_All_IP_Stat
Device_IP_to_MAC = IP_to_MAC
Get_Gateway = Get_GW

def ignore(*args):
    pass