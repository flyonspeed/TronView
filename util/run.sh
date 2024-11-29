#!/bin/bash
# Run TronView with a menu for selecting demos and options
# using dialog to build menus.  https://man.uex.se/1/dialog
# Nov 22, 2024.  Topher.

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRONVIEW_DIR="$(dirname "$SCRIPT_DIR")"

# Create data directory if it doesn't exist
mkdir -p "$TRONVIEW_DIR/data"
mkdir -p "$TRONVIEW_DIR/data/system"

# Function to save last run configuration
save_last_run() {
    local name="$1"
    local args="$2"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local auto_run="$3"    
    echo "{
    \"name\": \"$name\",
    \"args\": \"$args\",
    \"timestamp\": \"$timestamp\",
    \"auto_run\": $auto_run
}" > "$TRONVIEW_DIR/data/system/last_run.json"
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

# Check if we're running on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    RUN_PREFIX=""
    echo "Activating venv at: $TRONVIEW_DIR/venv/bin/activate"
    source "$TRONVIEW_DIR/venv/bin/activate"
    which python3
else
    RUN_PREFIX="sudo"
fi

# kill any running python3 processes
#$RUN_PREFIX pkill -f 'python3'

# Load last run configuration if it exists
LAST_RUN_FILE="$TRONVIEW_DIR/data/system/last_run.json"
if [ -f "$LAST_RUN_FILE" ]; then
    # Add "Last Run" as first menu option
    if command -v jq &> /dev/null; then
        LAST_NAME=$(jq -r '.name' "$LAST_RUN_FILE")
        LAST_ARGS=$(jq -r '.args' "$LAST_RUN_FILE")
        LAST_TIME=$(jq -r '.timestamp' "$LAST_RUN_FILE")
        LAST_AUTO_RUN=$(jq -r '.auto_run' "$LAST_RUN_FILE")
    else
        # Basic parsing if jq not available
        LAST_NAME=$(grep -o '"name": *"[^"]*"' "$LAST_RUN_FILE" | cut -d'"' -f4)
        LAST_ARGS=$(grep -o '"args": *"[^"]*"' "$LAST_RUN_FILE" | cut -d'"' -f4)
        LAST_TIME=$(grep -o '"timestamp": *"[^"]*"' "$LAST_RUN_FILE" | cut -d'"' -f4)
        LAST_AUTO_RUN=$(grep -o '"auto_run": *"[^"]*"' "$LAST_RUN_FILE" | cut -d'"' -f4)
    fi
fi

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

################################################################################
################################################################################
## AUTO-RUN ???
# If there was a last run, show dialog to run it again
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

################################################################################
################################################################################
## MAIN MENU
# Show 1st level main menu
# Create menu options array
declare -a menu_options=(
    "MGL Demos" "MGL related demos and tests" 
    "Dynon Demos" "Dynon related demos"
    "Stratux Demos" "Stratux only demos"
    "IMU Tests" "IMU related tests (Pi only)"
    "Virtual IMU" "Virtual IMU demos"
    "Tests" "Tests"
)
if [ -f "$LAST_RUN_FILE" ]; then
    menu_options=("Last Run" "Run last: $LAST_NAME" "${menu_options[@]}")
fi

while true; do
    exec 3>&1
    DIALOG_TIMEOUT=0
    choice=$(dialog --clear \
                    --title "Startup script" \
                    --menu '\n
 _____             __     ___               \n
|_   _| __ ___  _ _\ \   / (_) _____      __\n
  | || '"'"'__/ _ \| '"'"'_ \ \ / /| |/ _ \ \ /\ / /\n
  | || | | (_) | | | \ V / | |  __/\ V  V / \n
  |_||_|  \___/|_| |_|\_/  |_|\___| \_/\_/  \n
\n
                    Choose option:' 22 70 10 \
                    "${menu_options[@]}" \
                    2>&1 1>&3)
    exit_status=$?
    exec 3>&-
    
    handle_menu_exit $exit_status "main" || exit 0

    # Handle main menu selection
    case $choice in
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
                            choice="-i serial_mgl --playfile1 mgl_8.dat --in2 stratux_wifi --playfile2 stratux_8.dat --in3 gyro_virtual"
                            selected_name="MGL + Stratux + vIMU - chasing traffic"
                            ;;
                        2) 
                            choice="-i serial_mgl -c MGL_G430_Data_3Feb19_v7_Horz_Vert_Nedl_come_to_center.bin"
                            selected_name="MGL - G430 CDI"
                            ;;
                        3) 
                            choice="-i serial_mgl -c mgl_data1.bin"
                            selected_name="MGL - Gyro Test"
                            ;;
                        4) 
                            choice="-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat --in3 gyro_virtual"
                            selected_name="MGL + Stratux RV6 Chase 1"
                            ;;
                        5) 
                            choice="-i serial_mgl --playfile1 mgl_chase_rv6_2.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_2.dat --in3 gyro_virtual"
                            selected_name="MGL + Stratux RV6 Chase 2"
                            ;;
                        6) 
                            choice="-i serial_mgl --playfile1 mgl_chase_rv6_3.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_3.dat --in3 gyro_virtual"
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
                            choice="-i serial_d100 -e"
                            selected_name="Dynon D100"
                            ;;
                        2) 
                            choice="-i serial_skyview -e"
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
                                  "1" "Demo 54" \
                                  "2" "Demo 57 (Bad pitch/roll)" \
                                  "3" "Demo stratux_8 - Traffic targets only" \
                                  2>&1 1>&3)
                exit_status=$?
                exec 3>&-
                
                if handle_menu_exit $exit_status "sub"; then
                    case $subchoice in
                        1) 
                            choice="-i stratux_wifi -c stratux_54.dat"
                            selected_name="Demo 54"
                            ;;
                        2) 
                            choice="-i stratux_wifi -c stratux_57.dat"
                            selected_name="Demo 57 (Bad pitch/roll)"
                            ;;
                        3) 
                            choice="-i stratux_wifi -c stratux_8.dat"
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
                                  "1" "Live BNO055" \
                                  "2" "Live BNO055 & MGL" \
                                  "3" "Live BNO055 + MGL + Stratux" \
                                  "4" "Live dual BNO055" \
                                  "5" "Live BNO085" \
                                  "6" "Live BNO085 + MGL + Stratux" \
                                  2>&1 1>&3)
                exit_status=$?
                exec 3>&-
                
                if handle_menu_exit $exit_status "sub"; then
                    case $subchoice in
                        1) choice="-i gyro_i2c_bno055"
                            selected_name="Live BNO055"
                            ;;
                        2) choice="--in1 gyro_i2c_bno055 --in1 serial_mgl --playfile1 mgl_data1.bin"
                            selected_name="Live BNO055 & MGL"
                            ;;
                        3) choice="-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat --in3 gyro_i2c_bno055"
                            selected_name="Live BNO055 + MGL + Stratux"
                            ;;
                        4) choice="-i gyro_i2c_bno055 --in2 gyro_i2c_bno055"
                            selected_name="Live dual BNO055"
                            ;;
                        5) choice="-i gyro_i2c_bno085"
                            selected_name="Live BNO085"
                            ;;
                        6) choice="-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in3 stratux_wifi --playfile3 stratux_chase_rv6_1.dat --in2 gyro_i2c_bno085"
                            selected_name="Live BNO085 + MGL + Stratux"
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
            while true; do
                exec 3>&1
                subchoice=$(dialog --clear --title "Tests" \
                                  --menu "Choose a test:" 20 60 10 \
                                  "1" "Test Joystick" \
                                  "2" "Raw Serial Read" \
                                  "3" "Read Serial MGL" \
                                  "4" "Read Serial Dynon Skyview" \
                                  "5" "Read Serial Garmin G3x" \
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
                        --checklist "Select additional options:" 20 60 10 \
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
            today=$(date +%Y-%m-%d)
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
    else
        echo "IMU options only supported on Linux/Raspberry Pi"
    fi
fi

# Run the full command if it was set. example: python3 $TRONVIEW_DIR/util/tests/joystick.py
if [ ! -z "$FULL_COMMAND" ]; then
    eval "$FULL_COMMAND"
fi


echo "To run again type: ./util/run.sh (make sure you are in the TronView directory)"

