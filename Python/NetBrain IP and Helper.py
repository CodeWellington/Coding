#Used in NetBrain platform
import re
def ParseText(_original_result):
    config = _original_result.split("!")
    helper_dic = {}
    new_helper_dic = {}
    for line in config:
        if "interface Vlan" in line and "ip helper-address" in line:
            helper_dic[re.search(r"interface Vlan\d+", line).group()] = [re.search(r"ip address .+", line).group()] + re.findall(r"ip helper-address \S+", line)
    for key in helper_dic: #replace space with _ as netbrain can't have space on variable
        new_helper_dic[(re.sub(r"interface Vlan", "interface_Vlan", key))] = helper_dic[key]
    dic = {"svi": new_helper_dic}
    return dic
