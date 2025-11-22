from openpyxl.worksheet.table import Table, TableStyleInfo
from concurrent.futures import ThreadPoolExecutor
from openpyxl.styles import Border, Side, Font
from openpyxl import load_workbook
from getpass import getpass
import pandas as pd
import subprocess
import requests
import pyodbc
import json
import time
import re


# Reading file with hosts
def read_file():
    # Reading the config file
    while True:
        file = input("Enter the txt host file name to read: ")
        try:
            with open(file, "r", newline="") as host_file:
                host = host_file.readlines()
                host = [line.rstrip("\n\r") for line in host]  # Removing the \n\r
                return host
        except FileNotFoundError:
            print(f"No such file or directory: {file}")


def write_log(file_name):
    # Writing the log
    log_name = file_name.split(".")[0] + "_Logs.txt"
    with open(log_name, "a+") as write:
        for line in log_file:
            write.write(line + "\n")
    print(f"Log file: {log_name}")


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
def api_get(host, og_username, og_password, rest_api):
    # API information
    api_ver = 'v2'
    og_url = "https://%s" % host
    token = api_sessions(og_url, og_username, og_password, api_ver)

    # Info for excel output
    info_dict = {}
    service = ""
    columns = ["Device"]
    is_list = False

    if token:
        headers = {'Authorization': 'Token ' + token}
    else:
        return

    # Get info
    get_info = '/api/%s%s' %(api_ver, rest_api)

    # Retrieving JSON
    try:
        r_info = requests.get(og_url + get_info, headers=headers, verify=False)
        r_info.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return
    j_info = json.loads(r_info.text)


    # we might have different keys from the same api call
    for key, value in j_info.items():
        service = key
        if isinstance(value, list):
            for index in value:
                if isinstance(index, dict):
                    for inside_key in list(index.keys()):
                        if inside_key not in columns:
                            columns.append(inside_key)
                    is_list = True

        elif isinstance(value, dict):
            for inside_key in list(value.keys()):
                columns.append(inside_key)

    # Header
    df = pd.DataFrame(columns=columns)
    df.to_csv(file_name, index=False, mode="w+", header=True)

    if is_list:
        for index in range(len(j_info[service])):
            for column in columns:
                try:
                    info_dict[column] = [j_info[service][index][column]]

                except KeyError:
                    info_dict[column] = ["N/A"]

            info_dict["Device"] = host
            new_row = pd.DataFrame(info_dict)
            df = pd.concat([df, new_row], ignore_index=True)

    else:
        for column in columns:
            try:
                info_dict[column] = [j_info[service][column]]

            except Exception as e:
                info_dict[column] = ["N/A"]
        info_dict["Device"] = host
        new_row = pd.DataFrame(info_dict)
        df = pd.concat([df, new_row], ignore_index=True)
    return df


# Main loop
def main(host_file, file_name, rest_api):
    global log_file
    log_file = []


    og_username = input("Username: ")
    og_password = getpass()

    # Checking 20 devices per time
    with ThreadPoolExecutor(max_workers=40) as executor:
        future_to_device = {executor.submit(api_get, host, og_username, og_password, rest_api): host for host in host_file}

        all_dev = []
        # Process each result as they complete
        for future in future_to_device:
            try:
                all_dev.append(future.result())
            except Exception as e:
                log_file.append(str(e))

        for dev in all_dev:
            try:
                dev.to_csv(file_name, index=False, mode="a+", header=False)
            except Exception as e:
                log_file.append(str(e))
                pass
    write_log(file_name)


if __name__ == "__main__":
    start_time = time.perf_counter()
    host_file = read_file()
    file_name = str(input("Enter the output file name: ")) + ".csv"
    rest_api = input("Enter the Rest API (e.g. /monitor/lldp/neighbor): ")
    main(host_file, file_name, rest_api)
    print("Finished Main")
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Total time taken: {elapsed_time:.4f} seconds")
    print("Ending program...")
