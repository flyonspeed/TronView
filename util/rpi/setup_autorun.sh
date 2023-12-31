#!/bin/bash

pwd=${PWD}
runpathscript="${pwd//rpi/run_demo.sh}"
echo "Using startup script: $runpathscript"

# bookworm...
if grep -q bookworm "/etc/os-release"; then

	#uses wayland window manager..

	if grep -q tronview ~/.config/wayfire.ini; then
		echo "Already added to ~/.config/wayfire.ini"
		exit;
	fi

	#check if [autostart] is already in the ini file.
	if grep -q [autostart] ~/.config/wayfire.ini; then
		# doesn't exist.. so add it.
		echo "[autostart]" >> ~/.config/wayfire.ini
	fi
	
	# add the tronview startup script.
	sed -i "/\[autostart\]/a tronview\=${runpathscript}" ~/.config/wayfire.ini
	
	echo "Added startup script to ~/.config/wayfire.ini"

else
	# else older version that is user x11 instead of wayland

	sudo echo "@lxterminal -e $runpathscript" >> /etc/xdg/lxsession/LXDE-pi/autostart 
fi

