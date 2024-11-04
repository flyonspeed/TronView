#!/bin/bash

# make sure they are on macos
if [[ $(uname) != "Darwin" ]]; then
    echo "This script is only supported on macOS."
    exit 1
fi

echo "Setup mac osx for running software efis code"
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


# Create and activate virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Install python packages in virtual environment? (y or n)"
read -p " " yn;
case $yn in
    [Yy]* )
        echo "Installing packages in virtual environment..."
        python3 -m pip install pygame-ce==2.5.1
        python3 -m pip install serial
        python3 -m pip install pygame_menu
        python3 -m pip install MacTmp
        python3 -m pip install geographiclib
        python3 -m pip install numpy
        python3 -m pip install pygame_gui==0.6.10
        echo "Packages installed successfully in virtual environment"
        echo "To activate the virtual environment, run: source venv/bin/activate"
        ;;
    [Nn]* )echo "..."; 
esac

# Deactivate virtual environment
deactivate

