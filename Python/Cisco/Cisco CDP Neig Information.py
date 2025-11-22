import paramiko
import re
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

if __name__ == "__main__":
    hosts = ["host-a", "host-b"] #List of devices
    df = pd.DataFrame(columns=["Device", "Neighbor", "IP", "Platform"]) #Header
    df.to_csv(r"C:\path\test.csv", index=False, mode="a+") #Change the path as required, writing the header to csv file
    for host in hosts: #Looping tru the hosts
        try: #first try to access the devices
            config = ssh(host)
            config.send(b"show cdp neighbors  detail\n") #send the command to host
            time.sleep(1)
            log = str(config.recv(99999999).decode("utf-8")) #output of the config.send
            df["Device"] = [re.search(r"(\S+)#", log).group(1)] #device name
            log = log.split("-------------------------") #splitting the neighbors
            for device in log: #for each neighbor
                if "Device ID:" in device: #making sure it is a neighbor
                    try:  # try to find the neighbor - Device ID: <host>
                        df["Neighbor"] = re.search(r"Device ID: (\S+)", device).group(1)
                    except AttributeError:
                        df["Neighbor"] = "Not found"
                    try:  # try to find the ip - Entry address(es): \r\n  IP address: <x.x.x.x>
                        df["IP"] = re.search(r"Entry address\(es\):.+IP address: (.+?)\n", device, flags=re.DOTALL).group(1) #using the flags=re.DOTALL to include \r\n
                    except AttributeError:
                        df["IP"] = "Not found"
                    try:  # try to find the platform - Platform: <platform>,
                        df["Platform"] = re.search(r"Platform: (.+),", device).group(1)
                    except AttributeError:
                        df["Platform"] = "Not found"
                    df.to_csv(r"test.csv", index=False, mode="a+", header=False) #writhing a row to csv without the header
            print(f"Access to {host} OK")
        except paramiko.ssh_exception.NoValidConnectionsError:
            print(f"no Access to {host}")
