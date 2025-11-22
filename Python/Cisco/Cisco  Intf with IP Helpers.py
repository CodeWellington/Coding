import re
import time
import paramiko
from getpass import getpass


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
  

def inv_input(log):
    if "Invalid input" in log:
        time.sleep(1)
        print(f"Invalid input detected!\nEnding...")
        exit()
      

def config_block(file, regex):
    # Find the block of code based on regex - Ex. ap profile <name> [ap\sprofile\s.*]
    output = {}
    temp = ""

    for line in file:
        if temp and line.startswith(" "): # Config block starts with space
            output[temp].append(line)
        elif temp and not line.startswith(" "):
            temp = "" # When the block finishes

        try:
            temp = re.search(regex, line).group(1)
            output[temp] = []
        except:
            continue
    return output
  

def retrieving_info(host):
    # Sending the show command
    username = input("Username: ")
    password = getpass()
    intf = {}
    try:  # Try to access the devices
        show = ssh(host, username, password)
        print(f"Access to {host} OK")
        log = str(show.recv(99999999).decode("utf-8"))
        # try to send command
        try:
            # Checking the subnets
            show.send("show ip route connected\n")
            time.sleep(1)
            log = str(show.recv(99999999).decode("utf-8"))  # output of the show.send
            # If the input is invalid this script will stop
            inv_input(log)
            # Checking the intf and subnets vars
            output = log.splitlines()
            for line in output:
                sub_int = re.search(r"C\s+(\S+)\s+is\s+directly\s+connected,\s+(\S+)", line)
                if sub_int:
                    # Subnet is group(1) and intf is group(2)
                    intf[sub_int.group(2)] = {"Subnet": sub_int.group(1)}

            # Checking if there is ip helpers
            show.send("show run\n")
            time.sleep(5)
            log = str(show.recv(99999999).decode("utf-8"))
            # If the input is invalid this script will stop
            inv_input(log)
            # Checking the helpers vars
            output = log.splitlines()
            regex = "^interface\s+(\S+)"
            intf_block = config_block(output, regex)
            intf_w_helpers = {}

            # This is a dict, key is the intf and value each line under intf
            for key in intf_block:
                if any("ip helper-address" in item for item in intf_block[key]) and intf.get(key):
                    intf_w_helpers[key] = intf[key]
                    intf_w_helpers[key]["helper"] = True

            return intf_w_helpers
        except AttributeError:
            print("Error while sending the command.")

    except Exception as error: # If we can't access the device
        msg = f"\n{host} - {error}\n"
        print(msg)

host = str(input("Enter Hostname"))
intf_w_helpers = retrieving_info(host)

print(intf_w_helpers)


