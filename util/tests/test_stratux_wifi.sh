#!/bin/bash
# check if nc is installed
if ! command -v nc &> /dev/null
then
    # install nc depending on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install nc
    else
        sudo apt-get install -y netcat-traditional
    fi
fi

# check if hd is installed
if ! command -v hd &> /dev/null
then
	if [[ "$OSTYPE" == "darwin"* ]]; then
		# don't know how to install hd on macos
		echo "Running on macos"
	else
		# todo: install hd??
		echo "Running on linux"
	fi
fi

echo "-=-=- Test stratux or iLevil connection -=-=-"
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
echo "----------------------------------------"

case $char in
	[Uu]* )echo "Listening for iLevil UDP port 43211"
		if [[ "$OSTYPE" == "darwin"* ]]; then
			nc -lu 43211 | hexdump -C
		else
			nc -u -l -p 43211 -k | hd
		fi
		;;
	[Tt]* )echo "Listening for iLevil 192.168.1.1 TCP port 2000"
		if [[ "$OSTYPE" == "darwin"* ]]; then
			nc -zv 192.168.1.1 2000 | hexdump -C
		else
			nc -zv 192.168.1.1 2000 | hd
		fi
		;;
	[Ss]* )echo "Listening for Stratux UDP port 4000"
		if [[ "$OSTYPE" == "darwin"* ]]; then
			nc -lu 4000 | hexdump -C
		else
			nc -u -l -p 4000 -k | hd
		fi
		;;
    *) echo "Later skater!"
esac

