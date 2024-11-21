#!/bin/bash

# make sure they are on macos
if [[ $(uname) != "Darwin" ]]; then
    echo "This script is only supported on macOS."
    exit 1
fi

# Function to get user input with a prompt
get_input() {
    prompt="$1"
    # Print prompt to stderr and read from stdin
    echo "$prompt" >&2
    read response </dev/tty
    echo "$response"
}


echo "Setup mac osx for running TronView"
echo "-----------------------------------"

# check if homebrew is installed
if ! command -v brew &> /dev/null
then
    echo "Homebrew could not be found. Installing..."
	ruby -e '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)'
	echo export PATH='usr/local/bin:$PATH' >> ~/.bash_profile
	brew update
	brew doctor
fi

# check if python3 is installed
if ! command -v python3 &> /dev/null
then
	echo "Python3 could not be found. Installing..."
	brew install python3
fi

# Get absolute paths. remove 2 levels from the path because we are in util/macosx
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TRONVIEW_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
echo "TronView directory: $TRONVIEW_DIR"

# check if virtual environment is activated
if ! [[ "$VIRTUAL_ENV" ]]; then

	echo "Python Virtual environment is not activated. Creating venv..."
	python3 -m venv "$TRONVIEW_DIR/venv"
    source "$TRONVIEW_DIR/venv/bin/activate"
fi

yn=$(get_input "Install Python libraries required by TronView (macOS)?  (y or n)")
case $yn in
	[Yy]* )echo "Installing python libs"
		# install python libs in virtual environment
		echo "TronView directory: $TRONVIEW_DIR"
		python3 -m pip install -r "$TRONVIEW_DIR/util/macosx/requirements.txt"
		;;
	[Nn]* )echo "..."; 
esac


