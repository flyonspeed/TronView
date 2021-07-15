import re, subprocess
 
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
 
temp, msg = check_CPU_temp()
print(f"temperature {temp}°C")
print(f"full message {msg}")

