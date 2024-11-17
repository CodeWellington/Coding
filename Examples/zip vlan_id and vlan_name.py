import re
from pprint import pprint
show_vlan = """
VLAN  Name                             Status    Ports
----- -------------------------------- --------- -------------------------------
1     default                          active    Cpu, Et1, Et2, Et3, Et4, Et5
                                                 Et6, Et7
400   blue400                          active   
401   blue401                          active   
402   blue402                          active   
403   blue403                          active  
"""

output = show_vlan.splitlines()
vlan_id = []
vlan_name = []
for line in output:
    if re.search(r"^\d+", line):
        vlan_id.append(re.search(r"^\d+", line).group())
        vlan_name.append(re.search(r"^\d+\s+(\w+)\s", line).group(1))
bind_vlans = list(zip(vlan_id, vlan_name))
pprint(bind_vlans)
