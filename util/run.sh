#!/bin/bash
# Run TronView with a menu for selecting demos and options
# Nov 22, 2024.  Topher.

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRONVIEW_DIR="$(dirname "$SCRIPT_DIR")"

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
$RUN_PREFIX pkill -f 'python3'

# Create menu options array
declare -a menu_options=(
    "MGL Demos" "MGL related demos and tests" 
    "Dynon Demos" "Dynon related demos"
    "Stratux Demos" "Stratux only demos"
    "IMU Tests" "IMU related tests (Pi only)"
    "Virtual IMU" "Virtual IMU demos"
)

# Function to handle menu exit codes
handle_menu_exit() {
    local exit_status=$1
    if [ $exit_status -ne 0 ]; then  # Changed from -eq 1 to -ne 0
        if [ "$2" = "main" ]; then
            clear
            echo "Exiting..."
            exit 0
        else
            return 1  # Return to previous menu
        fi
    fi
    return 0
}

# Show 1st level main menu
while true; do
    exec 3>&1
    choice=$(dialog --clear \
                    --title "TronView" \
                    --menu '\n
 _____             __     ___               \n
|_   _| __ ___  _ _\ \   / (_) _____      __\n
  | || '"'"'__/ _ \| '"'"'_ \ \ / /| |/ _ \ \ /\ / /\n
  | || | | (_) | | | \ V / | |  __/\ V  V / \n
  |_||_|  \___/|_| |_|\_/  |_|\___| \_/\_/  \n
\n
                    Choose a category:' 20 60 10 \
                    "${menu_options[@]}" \
                    2>&1 1>&3)
    exit_status=$?
    exec 3>&-
    
    handle_menu_exit $exit_status "main" || exit 0

    # Handle main menu selection
    case $choice in
        ############################################################################
        "MGL Demos")
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
                    case $subchoice in
                        1) choice="-i serial_mgl --playfile1 mgl_8.dat --in2 stratux_wifi --playfile2 stratux_8.dat --in3 gyro_virtual" ;;
                        2) choice="-i serial_mgl -c MGL_G430_Data_3Feb19_v7_Horz_Vert_Nedl_come_to_center.bin" ;;
                        3) choice="-i serial_mgl -c mgl_data1.bin" ;;
                        4) choice="-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat --in3 gyro_virtual" ;;
                        5) choice="-i serial_mgl --playfile1 mgl_chase_rv6_2.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_2.dat --in3 gyro_virtual" ;;
                        6) choice="-i serial_mgl --playfile1 mgl_chase_rv6_3.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_3.dat --in3 gyro_virtual" ;;
                    esac
                    break  # Break just the inner loop
                else
                    choice=""  # Clear the choice
                    break  # Break the inner loop to return to main menu
                fi
            done
            ;;
        ############################################################################
        "Dynon Demos")
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
                        1) choice="-i serial_d100 -e" ;;
                        2) choice="-i serial_skyview -e" ;;
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
            while true; do
                exec 3>&1
                subchoice=$(dialog --clear --title "Stratux Demos" \
                                  --menu "Choose a demo:" 20 60 10 \
                                  "1" "Demo 54" \
                                  "2" "Demo 57 (Bad pitch/roll)" \
                                  "3" "Demo 5 - Traffic targets only" \
                                  2>&1 1>&3)
                exit_status=$?
                exec 3>&-
                
                if handle_menu_exit $exit_status "sub"; then
                    case $subchoice in
                        1) choice="-i stratux_wifi -c stratux_54.dat" ;;
                        2) choice="-i stratux_wifi -c stratux_57.dat" ;;
                        3) choice="-i stratux_wifi" ;;
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
                        1) choice="-i gyro_i2c_bno055" ;;
                        2) choice="--in1 gyro_i2c_bno055 --in1 serial_mgl --playfile1 mgl_data1.bin" ;;
                        3) choice="-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in2 stratux_wifi --playfile2 stratux_chase_rv6_1.dat --in3 gyro_i2c_bno055" ;;
                        4) choice="-i gyro_i2c_bno055 --in2 gyro_i2c_bno055" ;;
                        5) choice="-i gyro_i2c_bno085" ;;
                        6) choice="-i serial_mgl --playfile1 mgl_chase_rv6_1.dat --in3 stratux_wifi --playfile3 stratux_chase_rv6_1.dat --in2 gyro_i2c_bno085" ;;
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
            while true; do
                exec 3>&1
                subchoice=$(dialog --clear --title "Virtual IMU" \
                                  --menu "Choose a demo:" 20 60 10 \
                                  "1" "1 Virtual IMU" \
                                  "2" "2 Virtual IMUs" \
                                  2>&1 1>&3)
                exit_status=$?
                exec 3>&-
                
                if handle_menu_exit $exit_status "sub"; then
                    case $subchoice in
                        1) choice="--in1 gyro_virtual" ;;
                        2) choice="--in1 gyro_virtual --in2 gyro_virtual" ;;
                    esac
                    break  # Break just the inner loop
                else
                    choice=""  # Clear the choice
                    break  # Break the inner loop to return to main menu
                fi
            done
            ;;
    esac

    # If we have a valid choice, show additional options
    if [ ! -z "$choice" ]; then
        # Clear the dialog window
        clear

        # Additional options dialog
        exec 3>&1
        options=$(dialog --clear --title "Additional Options" \
                        --checklist "Select additional options:" 20 60 10 \
                        "text" "Run in text mode" OFF \
                        "multi" "Run multiple threads" OFF \
                        "debug" "Record debug output" OFF \
                        "auto" "Auto-run at startup" OFF \
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
            if [[ "$OSTYPE" != "linux-gnu"* ]]; then
                echo "Auto-run at startup only supported on Linux/Raspberry Pi"
            else
                # add the above args and startup command to .bashrc
                echo "alias tronview='sudo $TRONVIEW_DIR/util/run.sh'" >> ~/.bashrc
                echo "TronView will start automatically at login"
            fi
        fi

        # Break the main loop to run the command
        break
    fi
done

# Only run if we have a valid choice
if [ ! -z "$choice" ]; then
    # Clear the dialog window
    clear

    # Function to run python commands
    run_python() {
        cd "$TRONVIEW_DIR" || exit
        echo "Running from directory: $(pwd)"
        echo "Using Python: $(which python3)"
        eval "$RUN_PREFIX python3 $TRONVIEW_DIR/main.py $* $ADD_ARGS"
    }

    # Run the selected command
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ ! "$choice" =~ "bno" ]]; then
        run_python "$choice"
    else
        echo "IMU options only supported on Linux/Raspberry Pi"
    fi
fi

echo "To run again type: ./util/run.sh"

