import re
import time
import paramiko
import pandas as pd
from datetime import datetime
from getpass import getpass


def ssh(host, username, password):
    ###ssh client from paramiko###
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(username=username, password=password, hostname=host, port=22, timeout=30,  allow_agent=False, look_for_keys=False)
    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.invoke_shell()
    session.send('\r')
    time.sleep(2)
    return session


def read_file():
    ###Reading the config file###
    while True:
        file = input("Enter the Config File name to read: ")
        try:
            with open(file, "r", newline="") as config_file:
                config_file.readline()  # Reading Header
                configs = config_file.readlines()
                configs = [line.rstrip("\n") for line in configs]  # Removing the \n
                return configs
        except FileNotFoundError:
            print(f"No such file or directory: {file}")


def write_log(log_name, log_file):
    ###Writing the log###
    with open(log_name, "a+") as write:
        for line in log_file:
            write.write(line)
    print(f"Log file: {log_name}")


def dev_config(config_file):
    ###Preparing the configuration based on the input config file###
    """ Example of the input config file
    Configuration
    ############################################################
    !!!!!!!!!!!!!!!!!!!!!!hostname!!!!!!!!!!!!!!!!!!!!!!
    ############################################################
    config t
    Interface TenGigabitEthernet2/0/3
    description TEST1
    exit
    !
    Interface TenGigabitEthernet2/0/10
    description TEST2
    exit
    !
    end
    write
    !
    """
    hostname = ""
    devices = {}
    for line in config_file:
        if line.startswith("##"):
            continue
        elif line.startswith("!!!"):  # Finding hostnames
            try:
                hostname = re.search("!!!+(.+?)!", line).group(1)
                devices[hostname] = []
                continue
            except:
                print("The file has the Wrong Syntax to find the hostname!!!")
                exit()
        devices[hostname].append(line)  # Appending config
    return devices


def send_config(hosts):
    ###Sending the config to the devices###
    log_file = []
    username = input("Username: ")
    password = getpass()
    for host in hosts:  # Looping tru the hosts
        df["Device"] = [host]
        try:  # Try to access the devices
            config = ssh(host, username, password)
            print(f"Access to {host} OK")
            log = str(config.recv(99999999).decode("utf-8"))
            print(log)
            log_file.append(log)
            try:  # try to send config
                for configuration in devices_config[host]:
                    config.send(configuration)
                    time.sleep(1)
                    log = str(config.recv(99999999).decode("utf-8"))  # output of the config.send
                    log_file.append(log)
                    print(log)
                    ###If the input is invalid this script will stop###
                    if "Invalid input" in log:
                        time.sleep(1)
                        print(f"Invalid input detected! Check the log file.\nEnding...")
                        write_log(log_name, log_file)
                        exit()
                df["Status"] = ["Successful"]
            except AttributeError:
                df["Status"] = ["Error while sending the config."]

        except Exception as error: # If we can't access the device
            msg = f"\n{host} - {error}\n"
            print(msg)
            df["Status"] = [error]
            log_file.append(msg)

        df.to_csv(output, index=False, mode="a+", header=False)
    ###Writing the log###
    write_log(log_name, log_file)

if __name__ == "__main__":
    start_time = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    log_name = f"Log-{start_time}.txt"  #Log file
    output = f"Results-{start_time}.csv"  # Results in csv format
    
    df = pd.DataFrame(columns=["Device", "Status"])  #Header
    df.to_csv(output, index=False, mode="a+")  #Sending Header to csv
    
    ###Reading file###
    configs = read_file()
    
    ###Device Configuration###
    devices_config = dev_config(configs)
    
    ###Devices to access###
    hosts = devices_config.keys()
    
    ###Sending config to hosts###
    send_config(hosts)
