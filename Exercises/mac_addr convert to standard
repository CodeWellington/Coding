#Convert MAC to standard 00:62:EC:29:70:FE
def mac_list_converter(mac_list):
    mac = []
    for line in mac_list:
        mac_temp = line.upper().replace(".", "").replace("-", "").replace(":", "")
        counter = 1
        for l in mac_temp:
             mac.append(l)
             if counter % 2 == 0 and counter < 12:
                  mac.append(":")
             counter += 1
        mac.append("\n")
    mac_converted = "".join(mac)
    return mac_converted
