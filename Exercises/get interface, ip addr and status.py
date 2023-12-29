import paramiko
import re
import pandas as pd
import csv

def ssh(host):
    ssh_client = paramiko.SSHClient()  #ssh client from paramiko
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) #Helps when the key is unkow
    ssh_client.connect(username='admin', password='admin', hostname=host, port=22, timeout=60,  allow_agent=False, look_for_keys=False)
    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.invoke_shell()
    session.send('\r')
    time.sleep(2)
    return session

hosts = ["100.64.0.200", "100.64.0.201", "100.64.0.202"]  #List of devices
df = pd.DataFrame(columns=["Device", "INTERFACE", "IP-ADDRESS", "STATUS"]) #Header
df.to_csv("D:/IT/Python/Automation/test2.csv", index=False, mode="a+") #Change the path as required
time.sleep(2)
for host in hosts: #Looping tru the hosts
    try: # first try to access the devices
        config = ssh(host)
        config.send("show ip int bri\n")  #send the command tho host
        time.sleep(2)
        log = str(config.recv(99999999).decode("utf-8")) #output of the confi.send
        try: #try to find the interface
            intf = re.findall(r"\S+\d/\d", log) 
            df["INTERFACE"] = intf
        except ValueError:
            df["INTERFACE"] = "Not found"
        try: #try to find the ip address
            ip = re.findall(r"\S+\d/\d\s+(\S+)", log)
            df["IP-ADDRESS"] = ip
        except ValueError:
            df["IP-ADDRESS"] = "Not found"
        try: try to find the status
            status = re.findall(r"\S+\d/\d\s+\S+\s+\S+\s+\S+\s+(.....................)\s", log)
            df["STATUS"] = status
        except ValueError:
            df["STATUS"] = "Not found"
        df["Device"] = host
        print(f"Access to {host} OK")
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"no Access to {host}")
    finally: #write the information to csv
        df.to_csv("D:/IT/Python/Automation/test2.csv", index=False, mode="a+", header=False)
        time.sleep(2)
