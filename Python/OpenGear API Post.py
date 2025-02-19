from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from getpass import getpass
import requests
import json
import time


# Reading file with hosts
def read_file():
    # Reading the config file
    while True:
        file = input("Enter host file name to read: ")
        try:
            with open(file, "r", newline="") as host_file:
                host = host_file.readlines()
                host = [line.rstrip("\n\r") for line in host]  # Removing the \n\r
                return host
        except FileNotFoundError:
            print(f"No such file or directory: {file}")


def write_log(file_name):
    try:
        # Writing the log
        with open(file_name, "a+") as write:
            for line in log_file:
                write.write(line + "\n")
    except:
        pass


# API Session
def api_sessions(og_url, og_username, og_password, api_ver):
    requests.packages.urllib3.disable_warnings()
    token = False
    api_session = '/api/%s/sessions' % api_ver

    data = {'username': og_username, 'password': og_password}

    # Authenticating
    try:
        session = requests.post(og_url + api_session, data=json.dumps(data), verify=False)
        session.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\nAccess to %s as %s failed" % (og_url, og_username))
        print(e)
        log_file.append(str(e))
        return

    if json.loads(session.text)['state'] == 'authenticated':
        token = json.loads(session.text)['session']
        message = f"Authentication successful to {og_url}"
        print(message)
        log_file.append(message)
    else:
        message = f"Authentication to {og_url} failed!"
        print(message)
        og_file.append(message)
    return token


# API GET
def api_post(host, og_username, og_password, data):
    # API information
    api_ver = 'v2'
    og_url = "https://%s" % host
    token = api_sessions(og_url, og_username, og_password, api_ver)

    if token:
        headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    else:
        return

    # Get info
    post_path = '/api/%s/services/syslog' %api_ver
    # Retrieving JSON
    try:
        r_info = requests.post(og_url + post_path, data=json.dumps(data), headers=headers, verify=False)
        r_info.raise_for_status()
    except requests.exceptions.RequestException as e:
        log_file.append(str(e))
        print(e)
        return
    j_info = json.loads(r_info.text)
    print(j_info)



# Main loop
def main(host_file, file_name, data):
    global log_file
    log_file = []

    og_username = input("Username: ")
    og_password = getpass()

    # Checking 40 devices per time
    with ThreadPoolExecutor(max_workers=40) as executor:
        future_to_device = {executor.submit(api_post, host, og_username, og_password, data): host for host in host_file}

        all_dev = []
        # Process each result as they complete
        for future in future_to_device:
            try:
                all_dev.append(future.result())
            except Exception as e:
                log_file.append(str(e))

        for dev in all_dev:
            try:
                log_file.append(dev)
            except Exception as e:
                log_file.append(str(e))
                pass
    write_log(file_name)


if __name__ == "__main__":
    start_time = time.perf_counter()
    host_file = read_file()
    file_name = f"Log-{datetime.now().strftime('%Y_%m_%d-%H_%M_%S')}.txt"  # Log file
    # Enter the Rest API data
    rest_api = {

    }
    main(host_file, file_name, rest_api)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Total time taken: {elapsed_time:.4f} seconds")
    print(f"Log file name is: {file_name}")
    print("Ending program...")
