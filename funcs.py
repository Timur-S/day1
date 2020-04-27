from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException, NetMikoTimeoutException
import datetime
import yaml

#YAML config for Netmiko
devices_file='devices.yaml'
#Ntp server is my Ubuntu machine
NTP="192.168.184.10"
# IOS-XE-NTP=['ntp server '+NTP]



def get_current_date_and_time():
    """This function returns the formatted date and time"""
    now = datetime.datetime.now()
    return now.strftime("%Y_%m_%d-%H_%M_%S")

def get_name(device_dict):
    """This function returns hostname, IOS-XE and NXOS has different
       commands for hostname
    """
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        try:
            if device_dict['device_type'] == "cisco_ios":
                result = ssh.send_command("show running-config | s hostname").split()
                name=result[1]
            elif device_dict['device_type'] == "cisco_nxos":
                result = ssh.send_command("show hostname").split()
                name=result[0]
        except NetMikoAuthenticationException as a_error:
                print(a_error)
        except NetMikoTimeoutException as n_error:
                print(n_error)
    return name

def save_conf (device_dict):
    """Returns running config"""
    try:
        with ConnectHandler (**device_dict) as ssh:
                ssh.enable()
                result=ssh.send_command("show running-config")
                return result
    except NetMikoAuthenticationException as a_error:
        print(a_error)
    except NetMikoTimeoutException as n_error:
        print(n_error)

def cdp_info(device_dict):
    """ CDP information from devices, again IOS-XE and NXOS differ"""
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        try:
            if device_dict['device_type'] == "cisco_ios":
                result_cdp = ssh.send_command("show cdp | include enabled").split()
                result_neighbors = ssh.send_command("show cdp neighbors | include entries").split()
                status=result_cdp[-1]
                neighbors = result_neighbors[-1]
                if status == "enabled": cdp= "CDP is ON"
                else:
                    cdp = "CDP is OFF"
                total_neighbors= neighbors + "peers"
            elif device_dict['device_type'] == "cisco_nxos":
                result_cdp = ssh.send_command("show cdp global | include global").split()
                result_neighbors = ssh.send_command("show cdp neighbors | include entries").split()
                status = result_cdp[1]
                neighbors = result_neighbors[-1]
                if status == "enabled":
                    cdp = "CDP is ON"
                else:
                    cdp = "CDP is OFF"
                total_neighbors = neighbors + "peers"
        except NetMikoAuthenticationException as a_error:
                print(a_error)
        except NetMikoTimeoutException as n_error:
                print(n_error)
    return cdp, total_neighbors

def npe_check(device_dict):
    """Security Payload check"""
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        try:
            if device_dict['device_type'] == "cisco_ios":
                result = ssh.send_command("show version | include PE")
                if result:
                    security="PE"
                else:
                    security = "NPE"
            elif device_dict['device_type'] == "cisco_nxos":
                result = ssh.send_command("show version | include PE")
                if result:
                    security = "PE"
                else:
                    security = "NPE"
        except NetMikoAuthenticationException as a_error:
                print(a_error)
        except NetMikoTimeoutException as n_error:
                print(n_error)
    return security

def HW_check(device_dict):
    """Some software and hardware information"""
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        try:
            if device_dict['device_type'] == "cisco_ios":
                res_reload = ssh.send_command("show version | include reason").split()
                reason=res_reload[-1]
                res_hw = ssh.send_command("show platform | include Chassis").split()
                hw = res_hw[-1]
            elif device_dict['device_type'] == "cisco_nxos":
                res_reload = ssh.send_command("show version | include Reason").split()
                reason = res_reload[-1]
                res_hw = ssh.send_command(" show hardware | include Chassis | include :").split(":")
                hw = res_hw[-1].replace("\n", "").lstrip(" ")
        except NetMikoAuthenticationException as a_error:
                print(a_error)
        except NetMikoTimeoutException as n_error:
                print(n_error)
    return hw, reason

def set_ntp(device_dict):
    """Configure NTP if NTP server available"""
    with ConnectHandler(**device_dict) as ssh:
        ssh.enable()
        ping = ssh.send_command("ping "+NTP)
        if ping:
            ssh.config_mode()
            ntp=ssh.send_command("ntp server "+NTP)
            ntp_tz=ssh.send_command("clock timezone GMT 0 0")
            ssh.exit_config_mode()
            sh_ntp=ssh.send_command("show ntp status | include   synchronized")
            if sh_ntp:
                clock="Clock in Sync"
            else:
                clock = "Clock not Sync"
    return clock



