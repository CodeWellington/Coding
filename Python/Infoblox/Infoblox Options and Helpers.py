import getpass
import requests
import paramiko
import json
import time
import re

# user check
def user_info():
    check_cred = False
    while not check_cred:
        ddi_user = input("DDI Username: ")
        ddi_pwd = getpass.getpass()
        session = create_session(ddi_user, ddi_pwd)
        check_cred = get_requests(session, f"https://ddi.domain.com/wapi/v2.12.3/network?network=10.65.9.0/24&_return_fields=options")

    return ddi_user, ddi_pwd


def subnet_info():
    # Error handling for subnet manual input
    while True:
        try:
            subnet = input("Enter the subnet to search (e.g 10.65.9.0/24): ")
            re.search(r"\d+\.\d+\.\d+\.\d+/\d+", subnet).group(0)
            return subnet
        except Exception as e:
            print("Wrong syntax, please follow the example!")


def url_info(subnet):
    dhcp_options = f"https://ddi.domain.com/wapi/v2.12.3/network?network={subnet}&_return_fields=options"
    helpers = f"https://ddi.domain.com/wapi/v2.12.3/network?network={subnet}&_return_fields=network,members"
    return dhcp_options, helpers


def create_session(user, pwd):
    # Create a session object
    session = requests.Session()

    # Disable warnings for insecure connections
    requests.packages.urllib3.disable_warnings()

    # Set the authentication for the session
    session.auth = (user, pwd)

    return session


def get_requests(session, url):

    # Make the GET request using session
    response = session.get(url, verify=False)

    # Error handling http
    try:
        response.raise_for_status()
        # Parse the JSON response
        network_info = json.loads(response.text)
        return network_info

    except requests.exceptions.HTTPError:
        print("HTTPError - Could be Authorization Failed!")


def wapi(session, subnet):
    write = []
    url_dhcp, url_helpers = url_info(subnet)
    # Header string
    header = "-" * 50

    # Subnet information
    write.append(header)
    write.append(f'Subnet: {subnet}')

    # Option information
    dhcp_options = get_requests(session, url_dhcp)
    if dhcp_options:
        for i in dhcp_options:
            for option in i["options"]:
                write.append(f"    {option['name']}: {option['value']}")
    else:
        write.append(f"    Invalid subnet or no options configured for {subnet}!")

    # Helpers information
    helpers = get_requests(session, url_helpers)
    if helpers:
        for i in helpers:
            for helper in i["members"]:
                write.append(f"    ip helper-address {helper['ipv4addr']}")
    else:
        write.append(f"    Invalid subnet or no helpers configured for {subnet}!")

    write.append(header)

    return write


def interactive(session):

    # User input
    subnet = subnet_info()
    output = wapi(session, subnet)
    for line in output:
        print(line)


def read_txt():
    input_txt = []
    while True:
        file = str(input("Enter the input txt file path/name: ")) + ".txt"
        try:
            # Try to read the file
            with open(file, "r", newline="") as temp:
                input_txt_temp = temp.readlines()
                input_txt_temp = [row.rstrip("\r\n") for row in input_txt_temp]
                break
        except FileNotFoundError:
            print("No such file or directory!")

    for line in input_txt_temp:
        # Error handling for subnet txt input
        if re.search(r"\d+\.\d+\.\d+\.\d+/\d+", line):
            input_txt.append(line)
        elif not line:
            # Empty line - sometimes user keep last line blank
            pass
        else:
            print(f"Wrong syntax for {line}!\n"
                  f"Please fix it and try again\n"
                  f"Ending Program...")
            exit()
    return input_txt


def write_txt(output, file_name):
    # Writing to a txt file
    with open(file_name, "a+") as temp:
        for line in output:
            temp.write(f"{line}\n")


def ssh(host):
    while True:
        host_user = input("A-511 Username: ")
        host_pass = getpass.getpass()
        # ssh client from paramiko
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(username=host_user, password=host_pass, hostname=host, port=22, timeout=30,  allow_agent=False, look_for_keys=False)
            transport = ssh_client.get_transport()
            session = transport.open_session()
            session.invoke_shell()
            session.send('\r')
            time.sleep(2)
            return session
        except Exception as e:
            print(f"Access to {host} failed!")


def inv_input(log):
    # Invalid command
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
            temp = ""  # When the block finishes

        try:
            temp = re.search(regex, line).group(1)
            output[temp] = []
        except:
            continue
    return output


def retrieving_info(host):
    # Sending the show command
    intf = {}
    try:  # Try to access the devices
        show = ssh(host)
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


def main():
    # Credentials
    ddi_user, ddi_pwd = user_info()

    # Create a session
    session = create_session(ddi_user, ddi_pwd)

    while True:
        print("Please choose one option:\n"
              "1. Interactive\n"
              "2. Via txt\n"
              "3. Via device\n"
              "4. End program")
        int_or_txt = str(input("> "))
        if int_or_txt == "1":
            interactive(session)

        elif int_or_txt == "2":
            input_txt = read_txt()

            file_name = str(input("Enter the output txt file path/name: ")) + ".txt"
            if input_txt:
                for line in input_txt:
                    output = wapi(session, line)
                    write_txt(output, file_name)
                print(f"Completed! Your output file name is {file_name}.")

        elif int_or_txt == "3":
            host = input("Enter the hostname: ")
            intf_w_helpers = retrieving_info(host)
            for intf in intf_w_helpers:
                print("-" * 50)
                print(intf)
                output = wapi(session, intf_w_helpers[intf]["Subnet"])
                for line in output:
                    print(line)
        elif int_or_txt == "4":
            exit()
        else:
            print("Invalid option!")


if __name__ == "__main__":
    main()
