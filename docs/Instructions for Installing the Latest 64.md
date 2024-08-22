**Instructions for Installing the Latest 64-bit Raspberry Pi OS on a Blank SD Card, and Setting Up TronView HUD Project**

**Step 1: Download the Latest Raspberry Pi OS**

1. **Visit the Official Raspberry Pi Website:**  
   * Open your web browser and go to the Raspberry Pi OS download page.  
2. **Download the Raspberry Pi Imager:**  
   * Scroll down and click on the “Download for Windows/MacOS/Linux” button to download the Raspberry Pi Imager for your operating system.  
3. **Install the Raspberry Pi Imager:**  
   * Once downloaded, open the installer and follow the instructions to install the Raspberry Pi Imager on your computer.  
4. **Prepare Your SD Card:**  
   * Insert your blank SD card (at least 8GB) into your computer.  
5. **Write the Raspberry Pi OS to the SD Card:**  
   * Launch the Raspberry Pi Imager.  
   * Choose the OS: Select “Raspberry Pi OS (64-bit)” from the list.  
   * Choose the SD card: Select your SD card from the list of available drives.  
   * Click “Write” to begin writing the OS to the SD card. This process may take a few minutes.  
6. **Eject the SD Card:**  
   * Once the process is complete, safely eject the SD card from your computer.

**Step 2: Set Up Raspberry Pi and Install Support Programs**

1. **Boot Your Raspberry Pi:**  
   * Insert the SD card into your Raspberry Pi 5 and power it on.  
   * Follow the on-screen instructions to complete the initial setup (e.g., setting up Wi-Fi, localization settings, etc.).  
2. **Update the System:**  
   * Open a terminal on your Raspberry Pi and run the following commands to update the package list and upgrade installed packages:  
     Copy code and run in Python command line  
     sudo apt update  
     sudo apt upgrade \-y  
3. **Install Required Support Programs:**  
   * Install Python 3 and necessary development tools:  
     Copy code and run in Python command line  
     sudo apt install \-y python3-dev python3-pip  
   * Install additional dependencies required for the TronView project:  
     Copy code and run in Python command line  
     sudo apt install \-y libsdl1.2-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libgeographic-dev cmake  
   * Install Pygame:  
     Copy code and run in Python command line  
     sudo apt install \-y python3-pygame  
   * Install GeographicLib:  
     Copy code and run in Python command line  
     sudo apt install python3-geographiclib

**Step 3: Clone and Install the TronView HUD Project**

1. **Clone the TronView GitHub Repository:**  
   * Navigate to the home directory and clone the repository:  
     Copy code and run in Python command line  
     cd \~  
     **git clone [https://github.com/flyonspeed/TronView.git](http://\_blank)**  
2. **Install TronView Dependencies:**  
   * Navigate to the TronView directory:  
     Copy code and run in Python command line  
     **cd TronView**  
   * If there are any additional dependencies listed in the project’s documentation or requirements file, install them using pip:  
     Copy code and run in Python command line  
     **pip3 install \-r requirements.txt**  
3. **Run the TronView HUD Project:**  
   * You can now run the TronView HUD program by executing the following command:  
     Copy code and run in the Python command line  
     **sudo python3 main.py   to stop press the “q” key**    
4. **Set Up Automatic HUD program Start on Boot:**  
   * To ensure the TronView HUD starts automatically on boot, you can add a line to your “rc.local”  file in the /etc folder   
     Copy code and run in Python command line  
     “**cd /etc**”  
     “**sudo nano rc.local**”  
   * Add the line/lines below in rc.local after “**\# fi**” and before “**exit 0**”:  
      **/home/pi/start\_pygame.sh &  \# sets up Pi 5 cmd line graphics**  
      **/bin/sleep 2; cd /home/pi/TronView/ && sudo python3 main.py**   
     \# above auto starts HUD on bootup per config.cfg file  
        
      **/bin/sleep 2; cd /home/pi/TronView/ && sudo python3 main.py   \--in1 serial\_g3x \--playfile1 garmin\_g3x\_data1.txt**  
     \# above and lines below optional for demo playback of  
     \# of recorded HUD files stored in   
     \# TronView/lib/inputs/\_example\_data folder, HUD program will  
     \# sequence through each example with “**q**” key press  
     \# you do not need different config.cfg files for this mode  
     \# you can also playback 2 simultaneous (Serial & WIFI) files  
      **/bin/sleep 2; cd /home/pi/efis\_to\_hud/ && sudo python3 main.py**  
      **/bin/sleep 2; cd /home/pi/TronView/ && sudo python3 main.py \--in1 serial\_mgl \--playfile1 mgl\_11\_RV8Landing.dat**  
      **/bin/sleep 2; cd /home/pi/TronView/ && sudo python3 main.py \--in1 serial\_mgl \--playfile1 mgl\_8.dat \--in2 stratux\_wifi \--playfile2 stratux\_8.dat**  
       
   * Save rc.local with a ctrl-o (write-out) and exit with a ctrl-x.  Be very careful editing this file as it can cause boot up hangs and crashes if not correct.

**5\.   Reboot and Verify**

1. **Reboot Your Raspberry Pi:**  
   Copy code and run in Python command line  
   “**reboot**”  
2. **Verify the Installation:**  
   * After rebooting, your Raspberry Pi should automatically start the TronView HUD project.  
   * Verify that everything is working as expected.

This process should have you up and running with the latest Raspberry Pi OS and the TronView HUD project.

