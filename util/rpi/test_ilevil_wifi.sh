#!/bin/bash

echo "Test iLevil UDP or TCP connection ? (t or u)"
echo "For UDP, If hex data shows then its connected. Then hit cntrl-c to exit"
read -p " " yn;
case $yn in
	[Uu]* )echo "Listening on port 43211"
		sudo nc -u -l 0.0.0.0 43211 -k |hd
		;;
	[Tt]* )echo "checking TCP port 2000"
	       nc -zv 192.168.1.1 2000
	       ;;

	[Nn]* )echo "Later dude!."; exit;;
esac



