import pandas as pd
import requests
import json
import subprocess
import re
import pyodbc
from getpass import getpass
from openpyxl import load_workbook
from openpyxl.styles import Border, Side, Font
from openpyxl.worksheet.table import Table, TableStyleInfo




# Read CMDB from Database
def read_cmdb():
    server = 'xxxxxx'
    database = 'xxxxx'
    username = input("DB Username: ")
    password = getpass()
    Authentication = 'ActiveDirectoryPassword'
    driver = '{ODBC Driver 17 for SQL Server}'

    conn = pyodbc.connect('DRIVER=' + driver +
                          ';SERVER=' + server +
                          ';PORT=1433;DATABASE=' + database +
                          ';UID=' + username +
                          ';PWD=' + password +
                          ';AUTHENTICATION=' + Authentication
                          )
    print(f"Authentication to Database...")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, model_id_dv , location_dv , location_region, u_secondary_support_group_dv FROM snow.cmdb_ci WHERE sys_class_name = 'cmdb_ci_outofband_device' AND (manufacturer_dv LIKE '%open gear%' OR manufacturer_dv LIKE '%opengear%')")
    cmdb = {}
    for row in cursor.fetchall():
        cmdb[row[0]] = {"Model": row[1], "CMDB_Location": row[2], "CMDB_Region": row[3], "CMDB_Sec_Group": row[4]}
    return cmdb

# Main loop
def main(cmdb, file_name):
    API_VER = 'v3.7'
    API_SESSIONS = '/api/%s/sessions' % API_VER
    API_NODES_ENROLLED = '/api/%s/nodes?config:status=Enrolled' % API_VER

    lhaddress = "lighthouse.domain.com"
    lhusername = input("Lighthouse Username: ")
    lhpassword = getpass()

    print("Authenticating to %s as %s" % (lhaddress, lhusername))

    LH5_URL = "https://%s" % lhaddress

    requests.packages.urllib3.disable_warnings()

    data = {'username': lhusername, 'password': lhpassword}
    #Authenticating
    try:
        r = requests.post(LH5_URL + API_SESSIONS, data=json.dumps(data), verify=False)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        print("\nAuthentication to %s as %s failed" % (LH5_URL, lhusername))
        print(e)
        exit(1)
    if json.loads(r.text)['state'] == 'authenticated':
        token = json.loads(r.text)['session']
        print("Authentication successful")
    else:
        print("Authentication failed - exiting")
        exit(99)

    headers = {'Authorization': 'Token ' + token}
    #Retreiving JSON
    try:
        print("Retrieving JSON...")
        r = requests.get(LH5_URL + API_NODES_ENROLLED, headers=headers, verify=False)
        r.raise_for_status()
        print("Retrieved successfully")
    except requests.exceptions.RequestException as e:
        print(e)
        exit(1)
    j = json.loads(r.text)
    #Header
    df = pd.DataFrame(columns=["Hostname", "Folder", "Session_Name", "Username", "Protocol", "Emulation"])
    df.to_csv(file_name, index=False, mode="a+", header=True)
    #Looping tru json
    node_count = len(j["nodes"])
    print(f"Found {node_count} nodes")
    for node in j["nodes"]:
        intf = []
        for row in node["interfaces"]:
            if "ipv4_addr" in row:
                if "192.168." not in row["ipv4_addr"] and "wan" not in row["name"] and "Cellular Modem" not in row[
                    "name"]:
                    intf.append(row["name"] + " " + row["ipv4_addr"])
                else:
                    continue
        #Running nslookup to check dns entry
        try:
            node_ip = re.search(r"\d+\.\d+\.\d+\.\d+", str(intf)).group(0)
        except:
            node_ip = "No"
        x = str(subprocess.run(f"nslookup {node_ip}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True))
        try:
            dns = re.search(f"{node_ip}.+\d+\.\d+\.\d+\.\d+.+Name:\s+(\S+\.com)", x).group(1)
        except:
            dns = "Not found"

        #CMDB information

        for ci in cmdb:
            if ci.lower() == node["name"].lower():
                cmdb_model = cmdb[ci]["Model"]
                cmdb_location = cmdb[ci]["CMDB_Location"]
                cmdb_region = cmdb[ci]["CMDB_Region"]
                cmdb_sec_group = cmdb[ci]["CMDB_Sec_Group"]
                break
            else:
                cmdb_location = "Not found"
                cmdb_region = "Not found"
                cmdb_sec_group = "Not found"

        # Preparing the rows

        if dns == "Not found":
            hostname = node["name"].lower()
        else:
            hostname = dns

        # Checking the secondary group

        if cmdb_sec_group:
            if "commercial" in cmdb_sec_group.lower():
                esc = "CMM"
            elif "manufacturing" in cmdb_sec_group.lower():
                esc = "MFG"
            elif "data center" in cmdb_sec_group.lower():
                esc = "DC"
            elif "wan" in cmdb_sec_group.lower():
                esc = "WAN"
            elif "border" in cmdb_sec_group.lower():
                esc = "BOR"
            else:
                esc = "NOT"

        new_row = pd.DataFrame({
            "Hostname": [hostname],
            "Folder": f"OpenGear\{cmdb_region}\{cmdb_location}",
            "Session_Name": f"{hostname} - {esc} - {cmdb_model} - {node['firmware_version']} - {cmdb_location}",
            "Username": "a-deoliwx2",
            "Protocol": "SSH2",
            "Emulation": "Xterm"
        })
        df = pd.concat([df, new_row], ignore_index=True)
        # Counting down
        print(f"\rReading Device Number: {node_count}  ", end="")
        node_count -= 1
    df.to_csv(file_name, index=False, mode="a+", header=False)
    print(f"\nFile name is {file_name}")



if __name__ == "__main__":
    cmdb = read_cmdb()
    file_name = str(input("Enter the output file name: ")) + ".csv"
    sheet_name = "Lighthouse Inventory"
    main(cmdb, file_name)
    print("Ending program...")
