import re, subprocess
from sys import platform

def is_macosx():
    try:
        if platform == "darwin":
            # OS X
            return True
    except Exception: pass
    return False

# using MacTmp package.  https://pypi.org/project/MacTmp/
def check_CPU_temp():
    import MacTmp
    return float(MacTmp.CPU_Temp())

def check_GPU_temp():
    import MacTmp
    return MacTmp.GPU_Temp()

