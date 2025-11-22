import os
import csv
import paramiko
import maskpass
from scp import SCPClient
import traceback
import time

print("You will need the devices.csv and show_mac.tcl files!!!")
print("SCP must be enabled: 'ip scp server enable'")


while True:
    # Prompt user for action
    action = input("Do you want to 'save' files from devices or 'send' files to devices? (save/send): ").strip().lower()
    if action and  (action == "save" or action == "send"):
        break
    else:
        print("Invalid action. Please enter 'save' or 'send'.")


# Read device list from CSV file
device_pairs = []
csv_file = "Archive/devices.csv"
if os.path.exists(csv_file):
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        required_columns = {'from_device', 'to_device'}
        # Checking is the required columns are presented
        if not required_columns.issubset(reader.fieldnames):
            print(f"[ERROR] Local file {csv_file} missing required column name")
            print(f"Column name should be from_device and to_device instead of {reader.fieldnames}")
            print("Ending...")
            time.sleep(5)
            quit()

        # Gathering the pair of from and to
        for row in reader:
            if 'from_device' in row and 'to_device' in row:
                device_pairs.append((row['from_device'], row['to_device']))

elif not os.path.exists(csv_file):
    print(f"[ERROR] Local file {csv_file} not found.")
    print("Ending...")
    time.sleep(5)
    quit()


# Directory to save or read the files
working_dir = os.getcwd()

# Command to read the file from Cisco IOS
read_command = "more flash:mac_table.txt"

# Function for SSH credentials
def ssh_cred():
    username = input("Username: ")
    password = maskpass.askpass()
    return username, password


# Function to retrieve file from a device
def retrieve_mac_table(hostname):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, username=username, password=password, look_for_keys=False)

        stdin, stdout, stderr = ssh.exec_command(read_command)
        file_content = stdout.read().decode()
        error_output = stderr.read().decode()

        if "No such file" in file_content or "No such file" in error_output or "%Error opening" in file_content or not file_content.strip():
            print(f"[WARNING] File not found on {hostname}")
        else:
            normalized_content = file_content.replace('\r\n', '\n')
            filename = f"{hostname}_mac_table.txt"
            with open(os.path.join(working_dir, filename), "w") as f:
                f.write(normalized_content)
            print(f"[INFO] Saved mac_table.txt from {hostname} as {filename}")

        ssh.close()

    except Exception as e:
        print(f"[ERROR] Failed to connect to {hostname}: {e}")
        return str(e)



def send_files(from_hostname, to_hostname):
    local_mac_file = f"{from_hostname}_mac_table.txt"
    local_tcl_file = "show_mac.tcl"

    if not os.path.exists(local_mac_file):
        print(f"[ERROR] Local file {local_mac_file} not found. Skipping {to_hostname}.")
        return
    if not os.path.exists(local_tcl_file):
        print(f"[ERROR] Required file '{local_tcl_file}' not found in current directory.")
        return

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(to_hostname, username=username, password=password, look_for_keys=False)

        try:
            # Send MAC table
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(local_mac_file, remote_path="mac_table.txt")
                print(f"[INFO] Sent mac_table.txt to {to_hostname}")
        except Exception as e:
            print(f"[ERROR] Failed to send mac_table.txt to {to_hostname}: {e}")

        # Reopen the session to send the tcl file
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(to_hostname, username=username, password=password, look_for_keys=False)

        try:
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(local_tcl_file, remote_path="show_mac.tcl")
                print(f"[INFO] Sent show_mac.tcl to {to_hostname}")
        except Exception as e:
            print(f"[ERROR] Failed to send show_mac.tcl to {to_hostname}: {e}")

        ssh.close()

    except Exception as e:
        print(f"[ERROR] Failed to send all files to {to_hostname}: {e}")
        return str(e)

# SSH credentials
username, password = ssh_cred()

# Execute based on user action
if action == "save":
    for from_device, _ in device_pairs:
        count = 1
        while True:
            auth = retrieve_mac_table(from_device)
            if count > 2:
                break
            elif (auth and "Authentication failed" in auth):
                username, password = ssh_cred()
                count += 1
                pass
            else:
                break

elif action == "send":
    for from_device, to_device in device_pairs:
        count = 1
        while True:
            auth = send_files(from_device, to_device)
            if count > 2:
                break
            elif (auth and "Authentication failed" in auth):
                username, password = ssh_cred()
                count += 1
                pass
            else:
                break


# Keep the script open until the user presses Enter
try:
    while True:
        input("\nPress Enter to exit...")
        break
except KeyboardInterrupt:
    pass


