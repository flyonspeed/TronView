**Install Guide for Development on Windows (64-bit)  Aug 2024**

These steps will configure a Windows PC to allow development for the HUD project without needing an actual Raspberry Pi.

1. **Install Python 3.x (64-bit version):**  
   * Download and install the latest Python 3.x (64-bit) version for Windows from the official Python website:  
     * [Download Python 3.x](http://\_blank)  
   * During installation, ensure you check the option to "Add Python to PATH."  
2. **Install Pygame:**  
   * Pygame is a set of Python modules designed for writing video games, and it's necessary for the HUD project.  
   * Open Command Prompt (you can search for cmd in the Start menu) and run:  
     Copy code and run in Python command line  
     pip install pygame  
3. **Install PySerial:**  
   * PySerial is needed for serial communication, such as reading from and writing to serial ports.  
   * In the same Command Prompt, run:  
     Copy code and run in Python command line  
     pip install pyserial  
4. **Install Windows Curses (Required for Windows):**  
   * Windows doesn’t have native support for curses, so you'll need the windows-curses module to provide this functionality.  
   * Run the following command:  
     Copy code and run in Python command line  
     pip install windows-curses  
5. **Clone the HUD Project to Your Local Windows PC:**  
   * Now, clone the project repository to your local machine using Git. If you don't have Git installed, download and install it from [Git for Windows](http://\_blank).  
   * In Command Prompt, navigate to the directory where you want to store the project, then run:  
     Copy code and run in Python command line  
   * git clone [https://github.com/flyonspeed/TronView.git](http://\_blank)

   

   * Navigate to the project directory:  
     Copy code and run in Python command line  
     cd efis\_to\_hud  
6. **Adjust the Configuration for Windows:**  
   * To run the HUD project on Windows, you need to configure the hud.cfg file correctly, especially regarding the serial port settings.  
   * Open the hud.cfg file in a text editor and find the section for serial port configuration.  
   * Use the correct COM port (e.g., COM1, COM2, etc.) that is available on your Windows PC. You can find available COM ports by opening the **Device Manager** and expanding the **Ports (COM & LPT)** section.

**Running the HUD Project on Windows:**

* Once you have everything installed and configured, you can run the HUD project using Python:  
  Copy code and run in Python command line  
  python hud.py  
* You may not need to run the setup script meant for the Raspberry Pi (setup.sh), as those steps are specific to the Raspberry Pi environment.

**Notes:**

* **Development Differences on Windows vs. Raspberry Pi:**  
  * Be aware of slight differences in development and runtime behavior between Windows and Linux (Raspberry Pi). For example, sudo is not required on Windows, and path separators are different (backslashes \\ for Windows vs. forward slashes / for Linux).  
  * Ensure your code is portable and works across both environments by testing on the Raspberry Pi as well before deployment.

This guide should help you set up and develop the HUD project on a Windows PC without the need for an actual Raspberry Pi. Let me know if you encounter any issues or need further assistance\!

