from netmiko import ConnectHandler
from netmiko import NetMikoAuthenticationException, NetMikoTimeoutException
import yaml
from funcs import *

if __name__ == '__main__':
    with open(devices_file) as f:
         dev_list = yaml.safe_load(f)
         for device in dev_list:
             hostname =get_name(device)
             hardware, reboot =HW_check(device)
             NPE =npe_check(device)
             cdp, neighbors =cdp_info(device)
             ntp =set_ntp(device)
             config = save_conf(device)
             now_date=get_current_date_and_time()
             with open(hostname+now_date, 'w') as backup:
                 backup.write(config)
             print(hostname, hardware, reboot, NPE, cdp, neighbors, ntp, sep="|")






