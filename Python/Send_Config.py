
from concurrent.futures import ThreadPoolExecutor
import paramiko
import time
from datetime import datetime
from getpass import getpass
import pandas as pd

def ssh(host, username, password):
    # ssh client from paramiko
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(username=username, password=password, hostname=host, port=22, timeout=30,  allow_agent=False, look_for_keys=False)
    transport = ssh_client.get_transport()
    session = transport.open_session()
    session.invoke_shell()
    session.send('\r')
    time.sleep(2)
    return session


# Reading file with hosts
def read_host_file():
    while True:
        file = input("Enter the txt host file name to read: ")
        try:
            with open(file, "r", newline="") as host_file:
                host = host_file.readlines()
                host = [line.rstrip("\n\r") for line in host]  # Removing the \n\r
                return host
        except FileNotFoundError:
            print(f"No such file or directory: {file}")

# Reading the config file
def read_config_file():
    while True:
        file = input("Enter the Config File name to read: ")
        try:
            with open(file, "r", newline="") as config_file:
                configs = config_file.readlines()
                configs = [line.rstrip("\n") for line in configs]  # Removing the \n
                return configs
        except FileNotFoundError:
            print(f"No such file or directory: {file}")


def send_config(host, configs, username, password):
    # Sending the config to the devices
    log_file = []

    try:  # Try to access the devices
        config = ssh(host, username, password)
        #print(f"Access to {host} OK")
        log = str(config.recv(99999999).decode("utf-8"))
        #print(log)
        log_file.append(log)
        try:  # try to send config
            for configuration in configs:
                config.send(configuration)
                time.sleep(0.5)
                log = str(config.recv(99999999).decode("utf-8"))  # output of the config.send
                log_file.append(log)
                #print(log)
                if "Invalid input" in log:
                    message = "Invalid input"
                    print(f"{host} - {message}")
                    return message

        except Exception as error:
            message = error
            print(f"{host} - {message}")
            return  message

    except Exception as error: # If we can't access the device
        message = error
        print(f"{host} - {message}")
        return  message
    # if all is well
    message = "OK"
    print(f"{host} - {message}")
    return message


def main():
    output = f"Results-{start_time}.csv"  # Results in csv format
    df = pd.DataFrame(columns=["Device", "Status"])  # Header
    df.to_csv(output, index=False, mode="a+")  # Sending Header to csv

    host_file = read_host_file()
    configs = read_config_file()
    username = input("Username: ")
    password = getpass()

    # send the config 50 devices at a time
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_device = {executor.submit(send_config, host, configs, username, password): host for host in host_file}

        # Process each result as they complete
        for future in future_to_device:
            host = future_to_device[future]
            df["Device"] = [host]
            try:
                result = future.result()
                df["Status"] = [result]

            except Exception as e:
                df["Status"] = [e]

            df.to_csv(output, index=False, mode="a+", header=False)


start_time = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
start_counter = time.perf_counter()

main()

end_counter = time.perf_counter()
elapsed_time = end_counter - start_counter
print(f"Total time taken: {elapsed_time:.4f} seconds")

