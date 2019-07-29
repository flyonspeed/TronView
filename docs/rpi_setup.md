
# Raspberry Pi setup

The following is here to help getting the software running on your raspberry pi.

## Steps to get the HUD software running on Pi.
```
1.	If in the Windows like GUI Press ctrl+alt+f1 to quit from the GUI to the desktop 
2.	Type “sudo raspi-config”
3.	Select “boot options” -> desktop / cli -> "Console auto-login"
4.	Select "Advanced options" -> "Expand Filesystem"
5.	Select:  "OK"
6.	Select:  "Finish"
7.	Select:  "Yes"
8.	Wait for the reboot
9.	Enter “sudo raspi-config”
10.	Select:  "Network options" -> "WiFi"
11.	(If required) Choose your country. Pressing "u" will take you to USA.
12.	Enter your home WIFI network name and password.
13.	"Interfacing Options" -> "Enable SSH"
14.	(If Required) "Localization" -> "Change Keyboard Layout" -> "Generic 104"
        "Other" -> "English US" -> "Default" -> "No compose" -> "Yes"
15.	Select Boot Options
        B1 – AutoLogin
16.	Select:  Interfacing (to Select Serial/TTL Input)
        P6 – Serial
        NO – Login Shell
        Yes – Serial Port Hardware
17.	Select:  "Finish"
18.	Selecting/Changing Screen Resolution Type “sudo raspi-config”
        Select "Advanced options"
        Select A5 – Resolution  (Screen)  -> Recommend Default (Pi will Select resolution at BootUp)
        Select “OK”
        Select:  "Finish"
        Select:  "Yes"
19.	Wait for the reboot
20.	Install git command. This will let you get the latest source from github directly onto the pi.
        sudo apt-get -y install git
21.	To Check WIFI Connection:  Enter “ping google.com”. Press ctrl+c after a while. This will Confirm that you have internet access.   If no google.com then reset your wifi (see above) using raspi-config 
22.	Next clone the HUD development programs source from github
        Enter:  git clone https://github.com/dinglewanker/efis_to_hud.git
        GitHub will ask for your username/email & password.
        when done this will create a efis_to_hud dir
        Check PI directory by entering:   ls  (HUD directory programs should appear)
23.	Next you need to run the setup.sh script to finish install. This will setup serial port (if not all ready setup) and install the python libraries you need.
24.	Change to the correct sub-directory (efis_to_hud) by typing “cd efis_to_hud”
        then to run the script type   ./setup.sh
        It will take several minutes to complete the setup
        Next Reboot the PI. Enter:  reboot
25.	To input/playback (from separate PC)  External Recorded HUD Data start data playback into Serial-TTL Converter
26.	Next run the “serial_read.py” script to confirm correct data is being sent to the PI 
        Change directory back to “efis_to_hud”  dir then type Enter:  cd efis_to_hud
27.	Enter:  python serial_read.py
28.	Make sure the data is coming through and looks good.
29.	To exit enter cntrl-c
30.	To Run current HUD program enter “sudo python hud.py” (arguments as shown below will appear).

```

## How to auto run hud on start up

For making the hud automatically run when the raspberry pi boots up you will want to do the following.  (There are a few methods for doing this, but this one of the simplest)

Run the following from the command line. This will let you edit the crontab file.  Crontab is a tool that lets you run programs automatically at different times.  In this case we just want it to run the hud with the pi first boots up.

`sudo crontab -e`

When you do this the first time you may be asked which editor you want to use to edit cron.  Choose your favorite sword.

If you choose nano as your crontab editor.  Then hit cntrl-x and it will ask you if you want to save.  hit y to save.

Then add this next line to the top of the file.

`@reboot cd /home/pi/efis_to_hud/ &&  python hud.py`

Notice that this assumes you have installed the hud application in the efis_to_hud directory.  If you put it somewhere else then change this.

You can also pass different arguments to the hud.py script. For example if you want it to start in demo mode when it boots up.

`@reboot cd /home/pi/efis_to_hud/ &&  python hud.py -i serial_mgl -c MGL_V5.bin`

If you don't pass arguments it will try to use the hud.cfg file configuration on startup.  How to use this file is described later in this document.
 

## Speeding up boot up time on Pi.

Editing the /boot/config.txt with the following changes:

```
# Disable the rainbow splash screen
disable_splash=1

# Disable bluetooth 
dtoverlay=pi3-disable-bt

# Overclock the SD Card from 50 to 100MHz
# This can only be done with at least a UHS Class 1 card 
dtoverlay=sdtweak,overclock_50=100
 
# Set the bootloader delay to 0 seconds. The default is 1s if not specified. 
boot_delay=0

```

Make the kernel output less verbose by adding the "quiet" flag to the kernel command line in file /boot/cmdline.txt 

```
dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=PARTUUID=32e07f87-02 rootfstype=ext4 elevator=deadline fsck.repair=yes quiet rootwait
```
