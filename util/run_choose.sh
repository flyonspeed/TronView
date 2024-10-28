#!/bin/bash

# Check if we're running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    RUN_PREFIX=""
else
    # Assume Linux or other Unix-like OS
    RUN_PREFIX="sudo"
fi

$RUN_PREFIX pkill -f 'python3'

# ask user to choose which demo to run
echo "Choose which demo to run:"
echo "1. G3X - EFIS"
echo "2. G3X - AOA Test data"
echo "3. MGL & Stratux - chasing traffic"
echo "4. MGL - G430 CDI"
echo "5. MGL - Gyro Test"
echo "6. Dynon D100"
echo "7. Dynon Skyview"
echo "8. Stratux 5 Demo"
echo "20. live i2c bno085 data"
echo "21. live i2c bno055 data"
read -p "Enter your choice: " choice

if [ $choice -eq 1 ]; then
    $RUN_PREFIX python3 main.py -i serial_g3x -s F18_HUD -e
fi

if [ $choice -eq 2 ]; then
    $RUN_PREFIX python3 main.py -i serial_g3x -c g3x_aoa_10_99.dat -s F18_HUD
fi

if [ $choice -eq 3 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl --playfile1 mgl_8.dat --in2 stratux_wifi --playfile2 stratux_8.dat -s F18_HUD
fi

if [ $choice -eq 4 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl -c MGL_G430_Data_3Feb19_v7_Horz_Vert_Nedl_come_to_center.bin -s F18_HUD
fi

if [ $choice -eq 5 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl -c mgl_data1.bin -s F18_HUD
fi

if [ $choice -eq 6 ]; then
    $RUN_PREFIX python3 main.py -i serial_d100 -s F18_HUD -e
fi

if [ $choice -eq 7 ]; then
    $RUN_PREFIX python3 main.py -i serial_skyview -s F18_HUD -e
fi

if [ $choice -eq 8 ]; then
    $RUN_PREFIX python3 main.py -i stratux_wifi -c stratux_5.dat -s F18_HUD
fi

if [ $choice -eq 20 ]; then
    $RUN_PREFIX python3 main.py -i gyro_i2c_bno085 -s F18_HUD
fi

if [ $choice -eq 21 ]; then
    $RUN_PREFIX python3 main.py -i gyro_i2c_bno055 -s F18_HUD
fi
