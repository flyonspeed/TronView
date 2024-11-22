#!/bin/bash
# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRONVIEW_DIR="$(dirname "$SCRIPT_DIR")"


# Check if we're running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    RUN_PREFIX=""

    echo "Activating venv at: $TRONVIEW_DIR/venv/bin/activate"
    source "$TRONVIEW_DIR/venv/bin/activate"
    # Verify python path
    which python3

else
    # Assume Linux or other Unix-like OS
    RUN_PREFIX="sudo"
fi



# kill any running python3 processes
$RUN_PREFIX pkill -f 'python3'

# ask user to choose which demo to run
echo "Choose which demo/test to run:"
#echo "1:   G3X - EFIS"
#echo "2:   G3X - AOA Test data"
echo "3:   MGL & Stratux - chasing traffic, 4: MGL - G430 CDI, 5: MGL - Gyro Test"

echo "6:   Dynon D100"
echo "7:   Dynon Skyview"

echo "9, 10, or 11:   MGL & Stratux RV6 Chase 1, 2, or 3"

echo "12:  Stratux ONLY Demo 54"
echo "13:  Stratux ONLY Demo 57 (Bad pitch/roll)"
echo "14:  Stratux ONLY Demo 5 - Shows traffic targets only, No AHRS data"

echo "21:  live i2c bno055 IMU data (pi only)"
echo "22:  live i2c bno055 & MGL ( pi only)"
echo "23:  live i2c bno055 + MGL + Stratux (pi only)"
echo "24:  live dual bno055 + bno055 (pi only)"

echo "200: live bno085 IMU data (pi only)"
echo "201: live bno085 + MGL + Stratux (pi only)"
echo "205: bno085 DEMO DATA"


echo "Type 't' after number to run in text mode. Example: 3t"
echo "Type 'm' after number to run multiple threads for inputs. Example: 3m"
echo "Type 'd' to record console debug output to a file. Example: 3d (saves to data/console_logs/)"

get_input() {
    prompt="$1"
    echo "$prompt" >&2
    read response </dev/tty
    echo "$response"
}

choice=$(get_input "Enter your choice: ")

ADD_ARGS=""

# check if the user typed 't' after the number
if [[ $choice == *t ]]; then
    choice=${choice%t}
    ADD_ARGS="-t"
else
    # default to showing HUD
    ADD_ARGS="-s F18_HUD"
fi

# check if "m" is anywhere in the string
if [[ $choice == *m ]]; then
    choice=${choice%m} # remove m from the string
    # append -m to the args
    ADD_ARGS="$ADD_ARGS --input-threads"
fi

# check if "d" is anywhere in the string
if [[ $choice == *d ]]; then
    choice=${choice%d} # remove d from the string
    # check data/console_logs/<year>-<month>-<day>-log_file.txt exists, if not create it.
    today=$(date +%Y-%m-%d)
    log_file="data/console_logs/$today-console.txt"
    if [ ! -f $log_file ]; then
        mkdir -p data/console_logs
        touch $log_file
    fi
    #ADD_ARGS="$ADD_ARGS 2>&1 >> $log_file"
    # check if tee is installed, if so then add it to the args. tee will let us see the output in the terminal as well as record it.
    if command -v tee &> /dev/null
    then
        echo "tee found"
        ADD_ARGS="$ADD_ARGS 2>&1 | tee -a $log_file"
        # else just append to the file
    else
        ADD_ARGS="$ADD_ARGS >> $log_file 2>&1"
    fi
fi

# if not a number, exit
if ! [[ $choice =~ ^[0-9]+$ ]]; then
    echo "No choice... exiting"
    # jump to end
    choice=0
fi


# Function to run python commands
run_python() {
    cd "$TRONVIEW_DIR" || exit
    echo "Running from directory: $(pwd)"
    echo "Using Python: $(which python3)"
    eval "$RUN_PREFIX python3 $TRONVIEW_DIR/main.py $* $ADD_ARGS"
}



########################################################
# G3x demos
########################################################

if [ $choice -eq 1 ]; then
    run_python "-i serial_g3x -e"
fi

if [ $choice -eq 2 ]; then
    run_python "-i serial_g3x -c g3x_aoa_10_99.dat"
fi

########################################################
# MGL demos
########################################################

if [ $choice -eq 3 ]; then
    run_python "-i serial_mgl --playfile1 mgl_8.dat --in2 stratux_wifi --playfile2 stratux_8.dat"
fi

if [ $choice -eq 4 ]; then
    run_python "-i serial_mgl -c MGL_G430_Data_3Feb19_v7_Horz_Vert_Nedl_come_to_center.bin"
fi

if [ $choice -eq 5 ]; then
    run_python "-i serial_mgl -c mgl_data1.bin"
fi

########################################################
# Dynon demos
########################################################

if [ $choice -eq 6 ]; then
    run_python "-i serial_d100 -e"
fi

if [ $choice -eq 7 ]; then
    run_python "-i serial_skyview -e"
fi

########################################################
# MGL & Stratux RV6 Chase demos
########################################################

if [ $choice -eq 9 ]; then
    run_python "-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat"
fi

if [ $choice -eq 10 ]; then
    run_python "-i serial_mgl --playfile1 mgl_chase_rv6_2.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_2.dat"
fi

if [ $choice -eq 11 ]; then
    run_python "-i serial_mgl --playfile1 mgl_chase_rv6_3.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_3.dat"
fi

########################################################
# Stratux ONLY demos
########################################################

if [ $choice -eq 12 ]; then
    run_python "-i stratux_wifi -c stratux_54.dat"
fi

if [ $choice -eq 13 ]; then
    run_python "-i stratux_wifi -c stratux_57.dat"
fi

if [ $choice -eq 14 ]; then
    run_python "-i stratux_wifi"
fi


########################################################
# IMU test Pi only
########################################################

if [ $choice -eq 21 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_python "-i gyro_i2c_bno055"
    else
        echo "Currently only supported on linux/raspberry pi"
    fi
fi

if [ $choice -eq 22 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_python "--in1 gyro_i2c_bno055 --in1 serial_mgl --playfile1 mgl_data1.bin"
    else
        echo "only supported on pi"
    fi
fi

if [ $choice -eq 23 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_python "-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat -s F18_HUD --in3 gyro_i2c_bno055"
    else
        echo "only supported on pi"
    fi
fi

if [ $choice -eq 24 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_python "-i gyro_i2c_bno055 --in2 gyro_i2c_bno055"
    else
        echo "only supported on pi"
    fi
fi


if [ $choice -eq 200 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_python "-i gyro_i2c_bno085"
    else
        echo "Currently only supported on linux/raspberry pi"
    fi
fi

if [ $choice -eq 201 ]; then
    # linux/raspberry pi only
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        run_python "-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in3 stratux_wifi --playfile3 stratux_chase_rv6_1.dat -s F18_HUD --in2 gyro_i2c_bno085"
    else
        echo "only supported on pi"
    fi
fi

if [ $choice -eq 205 ]; then
    run_python "--in1 gyro_i2c_bno085 -e"
fi

########################################################
# End of script
########################################################

echo "To run again type: ./util/run_choose.sh"

