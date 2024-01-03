import serial, re, subprocess, platform

def is_raspberrypi():
    try:
        print(platform.machine())
        if platform.machine() == 'armv7l':
            return True
        #with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
        #    if m.read().lower().startswith('raspberry pi',0,12): return True
    except Exception: pass
    return False

def raspberrypi_ver():
    try:
        with open('/proc/device-tree/model', 'r') as file:
            data = file.read().rstrip()
            return data
    except Exception: pass
    return "Unkown"

def check_CPU_temp():
    temp = None
    err, msg = subprocess.getstatusoutput('vcgencmd measure_temp')
    if not err:
        m = re.search(r'-?\d\.?\d*', msg)   # a solution with a  regex
        try:
            temp = float(m.group())
        except ValueError: # catch only error needed
            pass
    return temp, msg

def mount_usb_drive():
    global rpi_usb_drive_mount
    import os
    if is_raspberrypi() == False:
        return False
    partitionsFile = open("/proc/partitions")
    lines = partitionsFile.readlines()[2:]#Skips the header lines
    for line in lines:
        words = [x.strip() for x in line.split()]
        minorNumber = int(words[1])
        deviceName = words[3]
        if minorNumber % 16 == 0:
            path = "/sys/class/block/" + deviceName
            if os.path.islink(path):
                if os.path.realpath(path).find("/usb") > 0:
                    checkForDevice = "/dev/"+deviceName+"1"
                    if os.path.exists(checkForDevice)!=True:
                        checkForDevice = "/dev/"+deviceName
                    rpi_usb_drive_mount = checkForDevice
                    print (checkForDevice+" -> /mnt/usb")
                    os.system('mkdir /mnt/usb 2>/dev/null')
                    os.system("mount "+checkForDevice+" /mnt/usb 2>/dev/null")
                    return True
    return False

def unmount_usb_drive():
    global rpi_usb_drive_mount
    import os
    if is_raspberrypi() == False:
        return False
    os.system("umount "+rpi_usb_drive_mount+" /mnt/usb 2>/dev/null")
    return True

def list_serial_ports(printthem):

    # List all the Serial COM Ports on Raspberry Pi
    proc = subprocess.Popen(['ls /dev/tty[A-Za-z]*'], shell=True, stdout=subprocess.PIPE)
    com_ports = proc.communicate()[0]
    com_ports_list = str(com_ports).split("\\n") # find serial ports
    rtn = []
    for com_port in com_ports_list:
        if 'ttyS' in com_port:
            if(printthem==True): print(com_port)
            rtn.append(com_port)
        if 'ttyUSB' in com_port:
            if(printthem==True): print(com_port)
            rtn.append(com_port)
    return rtn


def is_server_available():
    import urllib.request
    host = "http://flyonspeed.org"
    urllib.request.urlopen(host)
    print(host+" available")
    return True

    # hostname = "flyonspeed.org"
    # response = os.system("ping -n 1 " + hostname)

    # err, msg = subprocess.getstatusoutput("ping -n 1 " + hostname)
    # if not err:
    #     m = re.search(r'-?\d\.?\d*', msg)   # a solution with a  regex
    #     try:
    #         temp = float(m.group())
    #     except ValueError: # catch only error needed
    #         pass
    # return temp, msg


    # if response == 0:
    #     return True 
    # else:
    #     return False


def get_thermal_temperature():
    thermal = subprocess.check_output(
        "cat /sys/class/thermal/thermal_zone0/temp", shell=True).decode("utf8")
    return float(thermal) / 1000.0

# uptime in seconds
def get_uptime():
    uptime = subprocess.check_output(
        "cat /proc/uptime", shell=True).decode("utf8")
    return float(uptime.split(" ")[0])

# returns load averages for 1, 5, and 15 minutes
def get_load_average():
    uptime = subprocess.check_output("uptime", shell=True).decode("utf8")
    load_average = uptime.split("load average:")[1].split(",")
    return list(map(float, load_average))

def get_kernel_release():
    return subprocess.check_output("uname -r", shell=True).decode("utf8").strip()

def get_full_os_name():
    import platform
    import os
    return os.name + " " + platform.system() + " " + str(platform.release())


 #returns total, free and available memory in kB
def get_memory_usage():
    meminfo = subprocess.check_output("cat /proc/meminfo", shell=True).decode("utf8").strip()        
    memory_usage = meminfo.split("\n")

    total_memory = [x for x in memory_usage if 'MemTotal' in x][0]
    free_memory = [x for x in memory_usage if 'MemFree' in x][0]
    available_memory = [x for x in memory_usage if 'MemAvailable' in x][0]

    total_memory = re.findall(r'\d+', total_memory)[0]
    free_memory = re.findall(r'\d+', free_memory)[0]
    available_memory = re.findall(r'\d+', available_memory)[0]

    data = {
        "total_memory": int(total_memory),
        "free_memory": int(free_memory),
        "available_memory": int(available_memory)
    }
    return data
