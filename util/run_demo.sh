#!/bin/bash

cd /home/pi/efis_to_hud
sudo pkill -f 'python3'
#sudo python3 hud.py -i serial_d100 -e

sudo python3 hud.py -i serial_g3x -s F18_HUD -e

#sudo python3 hud.py -i serial_mgl -s F18_HUD

