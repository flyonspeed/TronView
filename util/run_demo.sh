#!/bin/bash

cd /home/pi/efis_to_hud
sudo pkill -f 'python3'
sudo python3 hud.py -i serial_d100 -e


