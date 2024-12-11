# Memory % for last 5 minutes

file = """
SW-1#show memory statistics
Tracekey : 1#553367939f11ff7794276752ee588130   

                Head    Total(b)     Used(b)     Free(b)   Lowest(b)  Largest(b)
Processor  FF85BF2010   813753120   311386248   502366872   498572528   502099124
reserve P  FF85BF2068      102404          92      102312      102312      102312
 lsmpi_io  FF84DFE1A8     6295128     6294304         824         824         412
Critical   FF967A53E8     4194308          92     4194216     4194216     4194216
"""

def memory_in_percen(used, total):
    return used / total * 100

memory_output = file.splitlines()
for info in memory_output:
    if "Processor" in info:
        total_processor = int(info.split()[2])
        used_processor = int(info.split()[3])
    elif "reserve" in info:
        total_reserve = int(info.split()[3])
        used_reserve = int(info.split()[4])
    elif "lsmpi" in info:
        total_lsmpi = int(info.split()[2])
        used_lsmpi = int(info.split()[3])
    elif "Critical" in info:
        total_critical = int(info.split()[2])
        used_critical = int(info.split()[3])


processor_percen = memory_in_percen(used_processor, total_processor)
reserve_percen = memory_in_percen(used_reserve, total_reserve)
lsmpi_percen = memory_in_percen(used_lsmpi, total_lsmpi)
critical_percen = memory_in_percen(used_critical, total_critical)
