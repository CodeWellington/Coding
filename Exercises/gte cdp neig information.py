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

hosts = [ "100.64.0.200", "100.64.0.201", "100.64.0.202"]
df = pd.DataFrame(columns=["Device", "Neighbor", "IP-ADDRESS", "Platform"])
df.to_csv("D:/IT/Python/Automation/test3.csv", index=False, mode="a+")
time.sleep(2)
for host in hosts:
    try:
        config = ssh(host)
        config.send(b"show cdp neighbors  detail\n")
        time.sleep(2)
        log = str(config.recv(99999999).decode("utf-8"))
        if "--More--" in log:
            config.send(" ")
            time.sleep(2)
            log += str(config.recv(99999999).decode("utf-8"))
        try:
            neig = re.findall(r"Device ID: (\S+)", log)
            df["Neighbor"] = neig
        except ValueError:
            df["Neighbor"] = "Not found"
        try:
            ip = re.findall(r"Entry address\(es\): \r\n  IP address: (\d+\.\d+\.\d+\.\d+)", log, flags=re.DOTALL)
            df["IP-ADDRESS"] = ip
        except ValueError:
            df["IP-ADDRESS"] = "Not found"
        try:
            platform = re.findall(r"Platform: (.+),", log)
            df["Platform"] = platform
        except ValueError:
            df["Platform"] = "Not found"
        df["Device"] = re.search(r"(\S+)#", log).group(1)
        print(f"Access to {host} OK")
    except paramiko.ssh_exception.NoValidConnectionsError:
        print(f"no Access to {host}")
    finally:
        df.to_csv("D:/IT/Python/Automation/test3.csv", index=False, mode="a+", header=False)
        time.sleep(2)
