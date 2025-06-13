import re

def sorting_vlan(mac_var):
    output = mac_var.splitlines()

    mac_table = []
    for line in output:
        if re.search(r"\S+\.", line):
            mac_table.append(line.rstrip())
    vlan = []
    for obj in mac_table:
        vlan.append(obj.split())
    for i in range(len(vlan)):
        vlan[i][0] = int(vlan[i][0])
    vlan.sort()
    print(f"{'Vlan':<10}{'Mac Address':20}{'Ports'}")
    for i in range(len(vlan)):
        print(f"{vlan[i][0]:<10}{vlan[i][1]:20}{vlan[i][3]}")

if __name__ == "__main__":
    mac_var = """
    sw1#sh mac address-table 
              Mac Address Table
    -------------------------------------------

    Vlan    Mac Address       Type        Ports
    ----    -----------       --------    -----
     100    01bb.c580.7000    DYNAMIC     Gi0/1
     200    0a4b.c380.7c00    DYNAMIC     Gi0/2
     300    a2ab.c5a0.700e    DYNAMIC     Gi0/3
     10     0a1b.1c80.7000    DYNAMIC     Gi0/4
     500    02b1.3c80.7b00    DYNAMIC     Gi0/5
     200    1a4b.c580.7000    DYNAMIC     Gi0/6
     300    0a1b.5c80.70f0    DYNAMIC     Gi0/7
     10     01ab.c5d0.70d0    DYNAMIC     Gi0/8
     1000   0a4b.c380.7d00    DYNAMIC     Gi0/9
    """
    sorting_vlan(mac_var)
