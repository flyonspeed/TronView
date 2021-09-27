import re, subprocess

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
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



#if is_raspberrypi() == True:
#    print("Running on Pi")
#else:
#    print("Not running on Pi")
#
#temp, msg = check_CPU_temp()
#print(f"temperature {temp}°C")
#print(f"full message {msg}")

