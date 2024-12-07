#!/bin/bash
# Run TronView with a menu for selecting demos and options
# using dialog to build menus.  https://man.uex.se/1/dialog
# Nov 22, 2024.  Topher.

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRONVIEW_DIR="$(dirname "$SCRIPT_DIR")"

if [[ "$OSTYPE" == "darwin"* ]]; then # Check if we're running on macOS
    RUN_PREFIX=""
else # else Linux we have to do everything as sudo so the app gets access to the serial ports and i2c
    RUN_PREFIX="sudo"
fi

# get version
VERSION=$(python3 -c "from lib.version import __version__; print(__version__)")
BUILD=$(python3 -c "from lib.version import __build__; print(__build__)")
BUILD_DATE=$(python3 -c "from lib.version import __build_date__; print(__build_date__)")
BUILD_TIME=$(python3 -c "from lib.version import __build_time__; print(__build_time__)")

RUN_MENU_AGAIN=true

# Create data directory if it doesn't exist
$RUN_PREFIX mkdir -p "$TRONVIEW_DIR/data"
$RUN_PREFIX mkdir -p "$TRONVIEW_DIR/data/system"

# Function to save last run configuration
save_last_run() {
    local name="$1"
    local args="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local auto_run="$3"    
    
    # Create the JSON content first
    local json_content='{
    "name": "'"$name"'",
    "args": "'"$args"'",
    "timestamp": "'"$timestamp"'",
    "auto_run": '"$auto_run"'
}'
    
    # Use tee with sudo to write the file
    echo "$json_content" | $RUN_PREFIX tee "$TRONVIEW_DIR/data/system/last_run.json" >/dev/null
    
    # check for success
    if [ $? -ne 0 ]; then
        echo "Error saving ($RUN_PREFIX) last run configuration to $TRONVIEW_DIR/data/system/last_run.json"
    fi
}

# Function to run python commands
run_python() {
    cd "$TRONVIEW_DIR" || exit
    echo "Running from directory: $(pwd)"
    echo "Using Python: $(which python3)"
    eval "$RUN_PREFIX python3 $TRONVIEW_DIR/main.py $* $ADD_ARGS"
}

# Check if dialog is installed
if ! command -v dialog &> /dev/null; then
    echo "dialog is not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install dialog
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get install dialog -y
    else
        echo "Please install dialog manually"
        exit 1
    fi
fi

# Check if we're running on macOS.  Create a python virtual environment and activate it.
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Activating venv at: $TRONVIEW_DIR/venv/bin/activate"
    source "$TRONVIEW_DIR/venv/bin/activate"
    which python3
fi

# kill any running python3 processes
#$RUN_PREFIX pkill -f 'python3'

# Function to load last run configuration
load_last_run() {
    LAST_RUN_FILE="$TRONVIEW_DIR/data/system/last_run.json"
    if [ -f "$LAST_RUN_FILE" ]; then
        # if jq in not installed then install it on linux
        if ! command -v jq &> /dev/null; then
            if [[ "$OSTYPE" == "linux-gnu"* ]]; then
                echo "jq is not installed. Installing..."
                sudo apt-get install jq -y
            fi
            if [[ "$OSTYPE" == "darwin"* ]]; then
                brew install jq
            fi
        fi

        # Load last run configuration
        if command -v jq &> /dev/null; then
            LAST_NAME=$(jq -r '.name' "$LAST_RUN_FILE")
            LAST_ARGS=$(jq -r '.args' "$LAST_RUN_FILE")
            LAST_TIME=$(jq -r '.timestamp' "$LAST_RUN_FILE")
            LAST_AUTO_RUN=$(jq -r '.auto_run' "$LAST_RUN_FILE")
        fi
    fi
}

# Function to handle menu exit codes
handle_menu_exit() {
    local exit_status=$1
    if [ $exit_status -ne 0 ]; then  # Changed from -eq 1 to -ne 0
        if [ "$2" = "main" ]; then
            #clear
            echo "Exiting..."
            exit 0
        else
            return 1  # Return to previous menu
        fi
    fi
    return 0
}

# Get a single character input without waiting for return
get_char() {
    # Save current terminal settings
    old_tty=$(stty -g)
    # Set terminal to raw mode
    stty raw -echo
    # Read single character
    char=$(dd if=/dev/tty bs=1 count=1 2>/dev/null)
    # Restore terminal settings
    stty "$old_tty"
    # Output the character
    echo "$char"
}

################################################################################
################################################################################
## AUTO-RUN ???
# If there was a last run, show dialog to run it again
load_last_run
# check if --skiplastrun is in the command line arguments
if [[ ! " $* " =~ "--skiplastrun" ]]; then
    if [ -f "$LAST_RUN_FILE" ] && [ "$LAST_AUTO_RUN" = "true" ]; then
        exec 3>&1
        dialog --clear \
               --title "TronView Auto-Run in 10 seconds" \
               --pause "\nRun TronView: $LAST_NAME\n\nPress OK to run again\nPress Cancel or ESC for menu" \
               12 60 10
        exit_status=$?
        exec 3>&-
        #echo "Last run exit status: $exit_status"
        case $exit_status in
            0)  # OK pressed or timeout
                choice="$LAST_ARGS"
                selected_name="$LAST_NAME"
                SHOW_ADDITIONAL_OPTIONS=false
                # Run the command immediately
                if [ ! -z "$choice" ]; then
                    run_python "$choice"
                fi
                exit 0
                ;;
            255)  # ESC pressed
                ;;
            1|*)    # Cancel/ESC pressed or any other result
                # Continue to main menu
                ;;
            esac
    fi
fi


################################################################################
################################################################################
## MAIN MENU
# Show 1st level main menu
# Create menu options array
    declare -a menu_options=(
        "Live Setup" "Live input setup options"
        "MGL Demos" "MGL related demos and tests" 
        "Dynon Demos" "Dynon related demos"
        "Stratux Demos" "Stratux only demos"
        "IMU Tests" "IMU related tests (Pi only)"
        "Virtual IMU" "Virtual IMU demos"
        "Tests" "Test scripts, Serial, Joystick, I2c, WIFI"
        "Update" "Update TronView & View Changelog"
    )


ASCII_ART='
_____             __     ___               \n
|_   _| __ ___  _ _\ \   / (_) _____      __\n
  | || '"'"'__/ _ \| '"'"'_ \ \ / /| |/ _ \ \ /\ / /\n
  | || | | (_) | | | \ V / | |  __/\ V  V / \n
  |_||_|  \___/|_| |_|\_/  |_|\___| \_/\_/  \n
'

# Check if glow is installed
if ! command -v glow &> /dev/null; then
    echo "glow is not installed. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install glow
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo mkdir -p /etc/apt/keyrings
        curl -fsSL https://repo.charm.sh/apt/gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/charm.gpg
        echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | sudo tee /etc/apt/sources.list.d/charm.list
        sudo apt update && sudo apt install glow
    fi
fi

while $RUN_MENU_AGAIN; do

    # make sure the last run is updated.  They could have just ran something and updated the json file
    load_last_run
    if [ -f "$LAST_RUN_FILE" ]; then
        menu_options_with_last_run=("Last Run" "$LAST_NAME" "${menu_options[@]}")
    else
        # else just use the normal menu options
        menu_options_with_last_run=("${menu_options[@]}")
    fi

    ################################################################################
    ################################################################################
    ## MAIN MENU
    # Show 1st level main menu
    while true; do
        exec 3>&1
        DIALOG_TIMEOUT=0
        choice=$(dialog --clear \
                        --title "Startup script" \
                        --menu "$ASCII_ART\nVersion: $VERSION Build: $BUILD $BUILD_DATE $BUILD_TIME" 22 70 10 \
                        "${menu_options_with_last_run[@]}" \
                        2>&1 1>&3)
        exit_status=$?
        exec 3>&-
        
        handle_menu_exit $exit_status "main" || exit 0

        # Handle main menu selection
        case $choice in
            ############################################################################
            "Live Setup")
                SHOW_ADDITIONAL_OPTIONS=true
                choice=""
                InputNum=0
                while [ $InputNum -lt 1 ]; do
                    exec 3>&1
                    options=$(dialog --clear --title "Input Options" \
                                --checklist "Use space bar to select 1 or more Inputs :" 20 60 10 \
                                "serial_mgl" "MGL Serial" OFF \
                                "serial_d100" "Dynon D100 Serial" OFF \
                                "serial_skyview" "Dynon Skyview Serial" OFF \
                                "serial_g3x" "Garmin G3x Serial" OFF \
                                "serial_grt_eis" "Grand Rapids EIS Serial" OFF \
                                "serial_nmea" "NMEA Serial" OFF \
                                "gyro_i2c_bno055" "BNO055 IMU i2c (Pi only)" OFF \
                                "gyro_i2c_bno055" "2nd BNO055 IMU i2c (Pi only)" OFF \
                                "gyro_i2c_bno085" "BNO085 IMU i2c (Pi only)" OFF \
                                "gyro_i2c_bno085" "2nd BNO085 IMU i2c (Pi only)" OFF \
                                "stratux_wifi" "Stratux WIFI Compatible Device" OFF \
                                "levil_wifi" "iLevil B.O.M WiFi (UDP)" OFF \
                                "gyro_virtual" "Virtual IMU" OFF \
                                "gyro_virtual" "2nd Virtual IMU" OFF \
                                "gyro_joystick" "Joystick vIMU" OFF \
                                "adc_ads1115" "Analog Input ADS1115 (Pi only)" OFF \
                                2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-

                    if handle_menu_exit $exit_status "sub"; then
                        # check if user selected any options
                        if [ -z "$options" ]; then
                            dialog --clear --title "Error" --msgbox "No inputs selected.  TronView needs at least one input selected." 10 60
                            choice=""                        
                        fi

                        InputNum=0
                        # Convert options to array using more compatible syntax
                        selected_opts=( $(echo "$options" | sed 's/"//g') )
                        
                        for opt in "${selected_opts[@]}"; do
                            # Skip if empty
                            [ -z "$opt" ] && continue
                            InputNum=$((InputNum+1))
                            choice="$choice --in$InputNum $opt"
                            selected_name="$selected_name $opt"
                        done
                        break
                    else
                        choice=""
                        break
                    fi

                done
                ;;

            ############################################################################
            "MGL Demos")
                SHOW_ADDITIONAL_OPTIONS=true
                while true; do
                    exec 3>&1
                    subchoice=$(dialog --clear --title "MGL Demos" \
                                      --menu "Choose a demo:" 20 60 10 \
                                      "1" "MGL + Stratux + vIMU - chasing traffic" \
                                      "2" "MGL - G430 CDI" \
                                      "3" "MGL - Gyro Test" \
                                      "4" "MGL + Stratux RV6 Chase 1" \
                                      "5" "MGL + Stratux RV6 Chase 2" \
                                      "6" "MGL + Stratux RV6 Chase 3" \
                                      2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-
                    
                    if handle_menu_exit $exit_status "sub"; then
                        selected_name=""
                        case $subchoice in
                            1) 
                                choice="--in1 serial_mgl --playfile1 mgl_8.dat --in2 stratux_wifi --playfile2 stratux_8.dat --in3 gyro_virtual"
                                selected_name="MGL + Stratux + vIMU - chasing traffic"
                                ;;
                            2) 
                                choice="--in1 serial_mgl -c MGL_G430_Data_3Feb19_v7_Horz_Vert_Nedl_come_to_center.bin"
                                selected_name="MGL - G430 CDI"
                                ;;
                            3) 
                                choice="--in1 serial_mgl -c mgl_data1.bin"
                                selected_name="MGL - Gyro Test"
                                ;;
                            4) 
                                choice="--in1 serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat --in3 gyro_virtual"
                                selected_name="MGL + Stratux RV6 Chase 1"
                                ;;
                            5) 
                                choice="--in1 serial_mgl --playfile1 mgl_chase_rv6_2.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_2.dat --in3 gyro_virtual"
                                selected_name="MGL + Stratux RV6 Chase 2"
                                ;;
                            6) 
                                choice="--in1 serial_mgl --playfile1 mgl_chase_rv6_3.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_3.dat --in3 gyro_virtual"
                                selected_name="MGL + Stratux RV6 Chase 3"
                                ;;
                        esac
                        break
                    else
                        choice=""
                        break
                    fi
                done
                ;;
            ############################################################################
            "Dynon Demos")
                SHOW_ADDITIONAL_OPTIONS=true
                while true; do
                    exec 3>&1
                    subchoice=$(dialog --clear --title "Dynon Demos" \
                                      --menu "Choose a demo:" 20 60 10 \
                                      "1" "Dynon D100" \
                                      "2" "Dynon Skyview" \
                                      2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-
                    
                    if handle_menu_exit $exit_status "sub"; then
                        case $subchoice in
                            1) 
                                choice="--in1 serial_d100 -e"
                                selected_name="Dynon D100"
                                ;;
                            2) 
                                choice="--in1 serial_skyview -e"
                                selected_name="Dynon Skyview"
                                ;;
                        esac
                        break  # Break just the inner loop
                    else
                        choice=""  # Clear the choice
                        break  # Break the inner loop to return to main menu
                    fi
                done
                ;;
            ############################################################################
            "Stratux Demos")
                SHOW_ADDITIONAL_OPTIONS=true
                while true; do
                    exec 3>&1
                    subchoice=$(dialog --clear --title "Stratux Demos" \
                                      --menu "Choose a demo:" 20 60 10 \
                                      "1" "Live Stratux Connection" \
                                      "2" "Demo Data 54" \
                                      "3" "Demo Data 57 (Bad pitch/roll)" \
                                      "4" "Demo Data stratux_8 - Traffic targets only" \
                                      2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-
                    
                    if handle_menu_exit $exit_status "sub"; then
                        case $subchoice in
                            1) choice="--in1 stratux_wifi"
                                selected_name="Live Stratux Connection"
                                ;;
                            2) 
                                choice="--in1 stratux_wifi -c stratux_54.dat"
                                selected_name="Demo 54"
                                ;;
                            3) 
                                choice="--in1 stratux_wifi -c stratux_57.dat"
                                selected_name="Demo 57 (Bad pitch/roll)"
                                ;;
                            4) 
                                choice="--in1 stratux_wifi -c stratux_8.dat"
                                selected_name="Demo stratux_8 - Traffic targets only"
                                ;;
                        esac
                        break  # Break just the inner loop
                    else
                        choice=""  # Clear the choice
                        break  # Break the inner loop to return to main menu
                    fi
                done
                ;;
            ############################################################################
            "IMU Tests")
                SHOW_ADDITIONAL_OPTIONS=true
                while true; do
                    exec 3>&1
                    subchoice=$(dialog --clear --title "IMU Tests" \
                                      --menu "Choose a test:" 20 60 10 \
                                      "1" "Live BNO055 IMU" \
                                      "2" "Live BNO055 IMU & MGL" \
                                      "3" "Live BNO055 IMU + MGL + Stratux" \
                                      "4" "Live dual BNO055 IMUs" \
                                      "5" "Live BNO085 IMU" \
                                      "6" "Live dual BNO085 IMUs + Live Stratux" \
                                      "7" "MGL + Stratux + Live BNO085" \
                                      "8" "vIMU + Live BNO085" \
                                      "9" "joystick vIMU + Live BNO085" \
                                      2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-
                    
                    if handle_menu_exit $exit_status "sub"; then
                        case $subchoice in
                            1) choice="--in1 gyro_i2c_bno055"
                                selected_name="Live BNO055"
                                ;;
                            2) choice="--in1 gyro_i2c_bno055 --in1 serial_mgl --playfile1 mgl_data1.bin"
                                selected_name="Live BNO055 & MGL"
                                ;;
                            3) choice="--in1 serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat --in3 gyro_i2c_bno055"
                                selected_name="Live BNO055 + MGL + Stratux"
                                ;;
                            4) choice="--in1 gyro_i2c_bno055 --in2 gyro_i2c_bno055"
                                selected_name="Live dual BNO055"
                                ;;
                            5) choice="--in1 gyro_i2c_bno085"
                                selected_name="Live BNO085"
                                ;;
                            6) choice="--in1 gyro_i2c_bno085 --in2 gyro_i2c_bno085 --in3 stratux_wifi"
                                selected_name="Live dual BNO085"
                                ;;
                            7) choice="--in1 serial_mgl --playfile1 mgl_chase_rv6_1.dat --in3 stratux_wifi --playfile3 stratux_chase_rv6_1.dat --in2 gyro_i2c_bno085"
                                selected_name="MGL + Stratux + Live BNO085"
                                ;;
                            8) choice="--in1 gyro_virtual --in2 gyro_i2c_bno085"
                                selected_name="vIMU + Live BNO085"
                                ;;
                            9) choice="--in1 gyro_joystick --in2 gyro_i2c_bno085"
                                selected_name="joystick vIMU + Live BNO085"
                                ;;
                        esac
                        break  # Break just the inner loop
                    else
                        choice=""  # Clear the choice
                        break  # Break the inner loop to return to main menu
                    fi
                done
                ;;
            ############################################################################
            "Virtual IMU")
                SHOW_ADDITIONAL_OPTIONS=true
                while true; do
                    exec 3>&1
                    subchoice=$(dialog --clear --title "Virtual IMU" \
                                      --menu "Choose a demo:" 20 60 10 \
                                      "1" "1 Virtual IMU" \
                                      "2" "2 Virtual IMUs" \
                                      "3" "Joystick vIMU + Virtual IMU" \
                                      2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-
                    
                    if handle_menu_exit $exit_status "sub"; then
                        case $subchoice in
                            1) choice="--in1 gyro_virtual"
                                selected_name="1 Virtual IMU"
                                ;;
                            2) choice="--in1 gyro_virtual --in2 gyro_virtual"
                                selected_name="2 Virtual IMUs"
                                ;;
                            3) choice="--in1 gyro_joystick --in2 gyro_virtual"
                                selected_name="Joystick vIMU + Virtual IMU"
                                ;;
                        esac
                        break  # Break just the inner loop
                    else
                        choice=""  # Clear the choice
                        break  # Break the inner loop to return to main menu
                    fi
                done
                ;;
            ############################################################################
            "Tests")
                SHOW_ADDITIONAL_OPTIONS=false
                choice=""
                while true; do
                    exec 3>&1
                    subchoice=$(dialog --clear --title "Tests" \
                                      --menu "Choose a test:" 20 60 10 \
                                      "1" "Test Joystick" \
                                      "2" "Raw Serial Read" \
                                      "3" "Read Serial MGL" \
                                      "4" "Read Serial Dynon Skyview" \
                                      "5" "Read Serial Garmin G3x" \
                                      "6" "Test Stratux and iLevil WiFi connection" \
                                      "7" "I2C Test (Pi only)" \
                                      2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-
                    
                    if handle_menu_exit $exit_status "sub"; then
                        case $subchoice in
                            1) FULL_COMMAND="python3 $TRONVIEW_DIR/util/tests/joystick.py" ;;
                            2) FULL_COMMAND="python3 $TRONVIEW_DIR/util/tests/serial_raw.py" ;;
                            3) FULL_COMMAND="python3 $TRONVIEW_DIR/util/tests/serial_read.py -m" ;;
                            4) FULL_COMMAND="python3 $TRONVIEW_DIR/util/tests/serial_read.py -s" ;;
                            5) FULL_COMMAND="python3 $TRONVIEW_DIR/util/tests/serial_read.py -g" ;;
                            6) FULL_COMMAND="$TRONVIEW_DIR/util/tests/test_stratux_wifi.sh" ;;
                            7) FULL_COMMAND="python3 $TRONVIEW_DIR/util/tests/i2c_test.py" ;;
                        esac
                        echo "Running: $FULL_COMMAND"
                        #exit 0
                        # goto the end of the loop
                        break 2
                    else

                        break  # Break the inner loop to return to main menu
                    fi
                done
                ;;
            ############################################################################
            "Update")
                SHOW_ADDITIONAL_OPTIONS=false
                choice=""
                # get current branch
                current_branch=$(git rev-parse --abbrev-ref HEAD)
                # get latest branch by date
                git fetch --all
                # remove HEAD -> from branch name (with extra spaces) if it exists 
                # and remove /origin/ from the beginning of the branch name
                latest_branch=$(git branch -r --sort=-committerdate | head -n 1 | sed 's/^.*origin\///' | sed 's/^HEAD -> //')
                # get date of latest branch
                latest_branch_date=$(git show -s --format=%ci $latest_branch)

                # get 3 latest branches
                latest_branch2nd=$(git branch -r --sort=-committerdate | head -n 2 | tail -n 1 | sed 's/^.*origin\///' | sed 's/^HEAD -> //')
                latest_branch2nd_date=$(git show -s --format=%ci $latest_branch2nd)

                latest_branch3rd=$(git branch -r --sort=-committerdate | head -n 3 | tail -n 1 | sed 's/^.*origin\///' | sed 's/^HEAD -> //')
                latest_branch3rd_date=$(git show -s --format=%ci $latest_branch3rd)

                # get 4th latest branch
                latest_branch4th=$(git branch -r --sort=-committerdate | head -n 4 | tail -n 1 | sed 's/^.*origin\///' | sed 's/^HEAD -> //')
                latest_branch4th_date=$(git show -s --format=%ci $latest_branch4th)

                while true; do
                    exec 3>&1
                    subchoice=$(dialog --clear --title "Update (via github)" \
                                      --menu "Choose:" 20 60 10 \
                                      "1" "Update TronView (current branch: $current_branch)" \
                                      "2" "View CHANGELOG.md" \
                                      "3" "Branch: $latest_branch ($latest_branch_date)" \
                                      "4" "Branch: $latest_branch2nd ($latest_branch2nd_date)" \
                                      "5" "Branch: $latest_branch3rd ($latest_branch3rd_date)" \
                                      "6" "Branch: $latest_branch4th ($latest_branch4th_date)" \
                                      2>&1 1>&3)
                    exit_status=$?
                    exec 3>&-

                    if handle_menu_exit $exit_status "sub"; then
                        RUN_AGAIN=false
                        case $subchoice in
                            1) FULL_COMMAND="git pull" 
                                RUN_AGAIN=true
                                ;;
                            2) 
                                if command -v glow &> /dev/null; then
                                    FULL_COMMAND="glow $TRONVIEW_DIR/CHANGELOG.md"
                                else
                                    FULL_COMMAND="less $TRONVIEW_DIR/CHANGELOG.md"
                                fi
                                break 2
                                ;;
                            3) FULL_COMMAND="git checkout $latest_branch && git pull" 
                                RUN_AGAIN=true
                                ;;
                            4) FULL_COMMAND="git checkout $latest_branch2nd && git pull" 
                                RUN_AGAIN=true
                                ;;
                            5) FULL_COMMAND="git checkout $latest_branch3rd && git pull" 
                                RUN_AGAIN=true
                                ;;
                            6) FULL_COMMAND="git checkout $latest_branch4th && git pull" 
                                RUN_AGAIN=true
                                ;;
                        esac
                        break 2
                    else
                        break
                    fi
                done
                ;;
            ############################################################################
            "Last Run")
                choice="$LAST_ARGS"
                SHOW_ADDITIONAL_OPTIONS=false
                break
                ;;
        esac

        ############################################################################
        # Additional Options Menu
        # If we have a valid choice, show additional options
        if [ ! -z "$choice"  ] && $SHOW_ADDITIONAL_OPTIONS; then
            # Clear the dialog window
            #clear

            # Additional options dialog
            exec 3>&1
            options=$(dialog --clear --title "Additional Options" \
                            --checklist "Use space bar to select 1 or more options :" 20 60 10 \
                            "text" "Run in text mode" OFF \
                            "multi" "Run multiple threads" OFF \
                            "debug" "Record debug output" OFF \
                            "auto" "Auto-run next time" OFF \
                            2>&1 1>&3)
            exit_status=$?
            exec 3>&-

            # If escape was pressed, go back to main menu
            if ! handle_menu_exit $exit_status "sub"; then
                choice=""
                continue  # Continue the main menu loop
            fi

            # Process additional options
            ADD_ARGS=""
            [[ $options == *"text"* ]] && ADD_ARGS="-t" || ADD_ARGS=""
            [[ $options == *"multi"* ]] && ADD_ARGS="$ADD_ARGS --input-threads"
            if [[ $options == *"debug"* ]]; then
                today=$(date +%Y-%m-%d_%H-%M-%S)
                log_file="data/console_logs/$today-console.txt"
                mkdir -p data/console_logs
                touch $log_file
                if command -v tee &> /dev/null; then
                    ADD_ARGS="$ADD_ARGS 2>&1 | tee -a $log_file"
                else
                    ADD_ARGS="$ADD_ARGS >> $log_file 2>&1"
                fi
            fi  

            if [[ $options == *"auto"* ]]; then
                # make sure we are on linux
                selected_auto_run="true"
            else
                selected_auto_run="false"
            fi

            # Before running the command, save the configuration
            if [ ! -z "$choice" ] && [ "$choice" != "$LAST_ARGS" ]; then
                save_last_run "$selected_name" "$choice $ADD_ARGS" "$selected_auto_run"
            fi

            # Break the main loop to run the command
            break
        fi
    done

    # Only run if we have a valid choice
    if [ ! -z "$choice" ]; then
        # Clear the dialog window
        #clear
        # Run the selected command
        if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ ! "$choice" =~ "bno" ]]; then
            run_python "$choice"
            exit_status=$?
            if [ $exit_status -ne 0 ]; then
                echo "[Error occurred. Press any key to continue...]"
                get_char
            fi
            # clear $choice
            choice=""
        else
            echo "IMU options only supported on Linux/Raspberry Pi"
            echo "[Press any key to continue...]"
            get_char
        fi
    fi

    # Run the full command if it was set. example: python3 $TRONVIEW_DIR/util/tests/joystick.py
    if [ ! -z "$FULL_COMMAND" ]; then
        eval "$FULL_COMMAND"
        echo "[Press any key to go back to the TronView menu]"
        get_char
        # clear $FULL_COMMAND
        FULL_COMMAND=""
        if $RUN_AGAIN; then  # if we need to run again, skip the last run
            exec "$0" "--skiplastrun"
            exit 0
        fi
    fi

done

echo "To run again type: ./util/run.sh (make sure you are in the TronView directory)"

