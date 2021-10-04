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


