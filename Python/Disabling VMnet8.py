###When doing labs, sometimes while on wireless you need to disable and re-enable the VMnet 8, which the is net intf for VMware

import subprocess
import time
print("Disabling the VMnet8...")
subprocess.run('netsh interface set interface "VMware Network Adapter VMnet8" admin=disabled', shell=True)
time.sleep(8)
subprocess.run('netsh interface show interface "VMware Network Adapter VMnet8"')
time.sleep(1)
print("Enabling VMnet8...")
subprocess.run('netsh interface set interface "VMware Network Adapter VMnet8" admin=enabled', shell=True)
subprocess.run('netsh interface show interface "VMware Network Adapter VMnet8"')
time.sleep(4)

##Convert this scrip to exe and run as admin

