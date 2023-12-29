import paramiko
import re
import csv
import pandas as pd
import time

def ssh(host):
    ssh_client = paramiko.SSHClient()  #ssh client from paramiko
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Helps when the key is unkown
    ssh_client.connect(username='admin', password='admin', hostname=host, port=22, timeout=60,  allow_agent=False, look_for_keys=False)
    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.invoke_shell()
    session.send('\r')
    time.sleep(2)
    return session

hosts = ["100.64.0.202", "100.64.0.201"] #List of devices
df = pd.DataFrame(columns=["Device", "Neighbor", "IP", "Platform"]) #Header
df.to_csv("D:/IT/Python/Automation/test3.csv", index=False, mode="a+") #Change the path as required, writing the header to csv file
time.sleep(1)
for host in hosts: #Looping tru the hosts
    log_temp = ""
    access = True #reseting the access to True
    try: #first try to access the devices
        config = ssh(host)
        config.send(b"show cdp neighbors  detail\n") #send the command tho host
        time.sleep(1)
        log = str(config.recv(99999999).decode("utf-8")) #output of the confi.send
        while True: #when you have lots of neighbors the --More-- will show up
            if "--More--" in log:
                config.send(" ")
                time.sleep(1)
                log_temp = str(config.recv(99999999).decode("utf-8")) #output after send the space command (not the sull output)
                log += log_temp #concatenate to keep the full output
            if "--More--" in log_temp: #checking if it needs to send another space command
                config.send(" ")
                time.sleep(1)
                log += str(config.recv(99999999).decode("utf-8"))  #concatenate to keep the full output
            else:
                break
        try: #try to find the neighbor - Device ID: <host>
            neig = re.findall(r"Device ID: (\S+)", log)
            df["Neighbor"] = neig
        except ValueError:
            df["Neighbor"] = "Not found"
        try: #try to find the ip - Entry address(es): \r\n  IP address: <x.x.x.x>
            ip = re.findall(r"Entry address\(es\): \r\n.+:\s(\d+\.\d+\.\d+\.\d+)", log)
            df["IP"] = ip
        except ValueError:
            df["IP-address"] = "Not found"
        try: #try to find the platform - Platform: <platform>,
            platform = re.findall(r"Platform: (.+),", log)
            df["Platform"] = platform
        except ValueError:
            df["Platform"] = "Not found"
        df["Device"] = re.search(r"(\S+)#", log).group(1)
        print(f"Access to {host} OK")
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"no Access to {host}")
        access = False #if inaccessible
    finally:
        if access: #if accessible write to csv
            df.to_csv("D:/IT/Python/Automation/test3.csv", index=False, mode="a+", header=False)
            time.sleep(1)
        else: # if inaccessible just pass
            pass
