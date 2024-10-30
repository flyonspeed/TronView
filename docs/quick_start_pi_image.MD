
## How to create a Raspberry Pi image for TronView

1) Download and install the [pi imager](https://www.raspberrypi.com/software/) to create an image of the latest Raspberry Pi OS. 

2) Choose Pi 4 or 5.  Which ever pi you have.

  ![cockpit1](screenshots/pi_imager1.png?raw=true)


3) Choose Raspberry Pi OS (64-bit) Debian Bookworm. (desktop)

  ![cockpit1](screenshots/pi_imager2.png?raw=true)

4) Choose a storage device.  Select the SD card you want to install the image to.  Then click Next.



5) Choose advanced options.  
 - Set a hostname (optional)
 - Enable SSH
 - Set a username and password (this will be your pi login
 - setup wifi (required!) You need to setup wifi before writing the image to the SD card. so you can continue with installing TronView.
 - Set timezone (recommended)

![cockpit1](screenshots/pi_imager3.png?raw=true)

6) Click Write.  This will take a while.  It will create a new SD card image.

Then you can continue with installing TronView.


## Manually setup wifi using raspi-config.

If you don't setup wifi in the imager, you can do it manually with raspi-config after you boot the pi.

If you want to do it manually, here is the link: https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

## Auto login to the pi console

Enter the command `sudo raspi-config` 

- System Options, Scroll down to S5 `Select Boot AutoLogin Console Autologin`

- select B2 `Console Autologin`.  

- Enter, then then TAB down to Select and Enter, Then Finish, then exit the configuration 

- Select Reboot.

