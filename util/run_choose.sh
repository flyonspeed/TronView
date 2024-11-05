#!/bin/bash

# Check if we're running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    RUN_PREFIX=""
    source venv/bin/activate
else
    # Assume Linux or other Unix-like OS
    RUN_PREFIX="sudo"
fi

$RUN_PREFIX pkill -f 'python3'

# ask user to choose which demo to run
echo "Choose which demo/test to run:"
#echo "1:  G3X - EFIS"
#echo "2:  G3X - AOA Test data"
echo "3:  MGL & Stratux - chasing traffic"
echo "4:  MGL - G430 CDI"
echo "5:  MGL - Gyro Test"

echo "6:  Dynon D100"
echo "7:  Dynon Skyview"

echo "9:  MGL & Stratux RV6 Chase 1"
echo "10: MGL & Stratux RV6 Chase 2"
echo "11: MGL & Stratux RV6 Chase 3"

echo "12: Stratux ONLY Demo 54"
echo "13: Stratux ONLY Demo 57 (Bad pitch/roll)"
echo "14:  Stratux ONLY Demo 5 - Shows traffic targets only, No AHRS data"

echo "20: live i2c bno085 IMU data (linux/raspberry pi only)"
echo "21: live i2c bno055 IMU data (linux/raspberry pi only)"
echo "Type 't' after number to run in text mode. Example: 3t"
read -p "Enter your choice: " choice

ADD_ARGS=""

# check if the user typed 't' after the number
if [[ $choice == *t ]]; then
    choice=${choice%t}
    ADD_ARGS="-t"
else
    # default to showing HUD
    ADD_ARGS="-s F18_HUD"
fi

# if not a number, exit
if ! [[ $choice =~ ^[0-9]+$ ]]; then
    echo "No choice... exiting"
    # jump to end
    choice=0
fi

########################################################
# G3x demos
########################################################

if [ $choice -eq 1 ]; then
    $RUN_PREFIX python3 main.py -i serial_g3x -e $ADD_ARGS
fi

if [ $choice -eq 2 ]; then
    $RUN_PREFIX python3 main.py -i serial_g3x -c g3x_aoa_10_99.dat $ADD_ARGS
fi

########################################################
# MGL demos
########################################################

if [ $choice -eq 3 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl --playfile1 mgl_8.dat --in2 stratux_wifi --playfile2 stratux_8.dat $ADD_ARGS
fi

if [ $choice -eq 4 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl -c MGL_G430_Data_3Feb19_v7_Horz_Vert_Nedl_come_to_center.bin $ADD_ARGS
fi

if [ $choice -eq 5 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl -c mgl_data1.bin $ADD_ARGS
fi

########################################################
# Dynon demos
########################################################

if [ $choice -eq 6 ]; then
    $RUN_PREFIX python3 main.py -i serial_d100 -e $ADD_ARGS
fi

if [ $choice -eq 7 ]; then
    $RUN_PREFIX python3 main.py -i serial_skyview -e $ADD_ARGS
fi

########################################################
# MGL & Stratux RV6 Chase demos
########################################################

if [ $choice -eq 9 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat $ADD_ARGS
fi

if [ $choice -eq 10 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl --playfile1 mgl_chase_rv6_2.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_2.dat $ADD_ARGS
fi

if [ $choice -eq 11 ]; then
    $RUN_PREFIX python3 main.py -i serial_mgl --playfile1 mgl_chase_rv6_3.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_3.dat $ADD_ARGS
fi

########################################################
# Stratux ONLY demos
########################################################

if [ $choice -eq 12 ]; then
    $RUN_PREFIX python3 main.py -i stratux_wifi -c stratux_54.dat $ADD_ARGS
fi

if [ $choice -eq 13 ]; then
    $RUN_PREFIX python3 main.py -i stratux_wifi -c stratux_57.dat $ADD_ARGS
fi

if [ $choice -eq 14 ]; then
    $RUN_PREFIX python3 main.py -i stratux_wifi $ADD_ARGS
fi


########################################################
# IMU test Pi only
########################################################

if [ $choice -eq 20 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        $RUN_PREFIX python3 main.py -i gyro_i2c_bno085 $ADD_ARGS
    else
        echo "Currently only supported on linux/raspberry pi"
    fi
fi

if [ $choice -eq 21 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        $RUN_PREFIX python3 main.py -i gyro_i2c_bno055 $ADD_ARGS
    else
        echo "Currently only supported on linux/raspberry pi"
    fi
fi

########################################################
# End of script
########################################################

echo "To run again type: ./util/run_choose.sh"

