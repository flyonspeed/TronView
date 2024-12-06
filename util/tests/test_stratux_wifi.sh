#!/bin/bash
# check if nc is installed
if ! command -v nc &> /dev/null
then
    # install nc depending on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install nc
    else
        sudo apt-get install -y netcat
    fi
fi

# check if hd is installed
if ! command -v hd &> /dev/null
then
	if [[ "$OSTYPE" == "darwin"* ]]; then
		# don't know how to install hd on macos
		echo "Running on macos"
	else
		sudo apt-get install -y hd
	fi
fi

# determine which hex dump command to use
if [[ "$OSTYPE" == "darwin"* ]]; then
    HEX_DUMP="hexdump -C"
else
    HEX_DUMP="hd"
fi


echo "Test stratux UDP connection Port 4000? "
echo "For UDP, If hex data shows then its connected. Then hit cntrl-c to exit"
echo "Press u for iLevil UDP port 43211"
echo "Press t for iLevil TCP port 2000"
echo "Press s for stratux UDP port 4000"

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

# Get input and process it
char=$(get_char | tr '[:upper:]' '[:lower:]')
printf "----------------------------------------\n"

case $char in
	[Uu]* )echo "Listening for iLevil UDP port 43211"
		sudo nc -u -l 0.0.0.0 43211 -k |$HEX_DUMP
		;;
	[Tt]* )echo "Listening for iLevil TCP port 2000"
	       nc -zv 192.168.1.1 2000 |$HEX_DUMP
	       ;;
	[Ss]* )echo "Listening for Stratux UDP port 4000"
		sudo nc -u -l 0.0.0.0 4000 -k |$HEX_DUMP
		;;
    *) echo "Later skater!"
esac

