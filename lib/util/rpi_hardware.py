import re, subprocess, platform

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
