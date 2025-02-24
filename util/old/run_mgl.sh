#!/bin/bash

cd /home/pi/efis_to_hud
#sudo pkill -f 'python3'
#sudo python3 main.py -i mgl_serial -e

#sudo python3 main.py -i serial_g3x -s F18_HUD -e

python3 main.py -i serial_mgl -s F18_HUD -e

