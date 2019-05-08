
# Optional Pi Instructions 
Following install guide if you need help. https://www.raspberrypi.org/documentation/installation/installing-images/README.md   Setup your serial input using the GPIO pins on pi zero. This page will help you. https://www.instructables.com/id/Read-and-write-from-serial-port-with-Raspberry-Pi/

Step by Step Set-Up Guidelines HUD Project Raspberry Pi Computer

1-	First – Download and UnZip “Raspbian-Stretch (desktop)” SD image (its a very large file) for pi. Latest can be gotten here. https://downloads.raspberrypi.org/raspbian_latest

2-	Download and install Etcher to help you Flash the Raspian OS to a Micro SD Card (recommend 16GB card)  https://www.balena.io/etcher/

3-	Next Using the Etcher Utility Flash the Raspian OS to your SD Card, its pretty easy but instructions are at https://www.raspberrypi.org/magpi/pi-sd-etcher/

4-	Put SD card in Raspberry Pi, then connect Power, USB Keyboard, & HDMI output to Regular Computer Monitor, (optional for now is the TTL/RS232 converter)

5-	Turn on power and watch as Pi boots up into a Windows Desktop like configuration

## Steps to get the HUD software running
1.	If in the Windows like GUI Press ctrl+alt+f1 to quit from the GUI to the desktop 
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
1.	"Other" -> "English US" -> "Default" -> "No compose" -> "Yes"
15.	Select Boot Options
1.	1. B1 – AutoLogin
16.	Select:  Interfacing (to Select Serial/TTL Input)
1.	P6 – Serial
2.	NO – Login Shell
3.	Yes – Serial Port Hardware
17.	Select:  "Finish"
18.	Selecting/Changing Screen Resolution Type “sudo raspi-config”
1.	Select "Advanced options"
2.	Select A5 – Resolution  (Screen)  -> Recommend Default (Pi will Select resolution at BootUp)
3.	Select “OK”
4.	Select:  "Finish"
5.	Select:  "Yes"
19.	   Wait for the reboot
20.	Install git command. This will let you get the latest source from github directly onto the pi.
1.	sudo apt-get -y install git
21.	To Check WIFI Connection:  Enter “ping google.com”. Press ctrl+c after a while. This will Confirm that you have internet access.   If no google.com then reset your wifi (see above) using raspi-config 
22.	Next clone the HUD development programs source from github
1.	Enter:  git clone https://github.com/dinglewanker/efis_to_hud.git
2.	GitHub will ask for your username/email & password.
3.	when done this will create a efis_to_hud dir
4.	Check PI directory by entering:   ls  (HUD directory programs should appear)
23.	Next you need to run the setup.sh script to finish install. This will setup serial port (if not all ready setup) and install the python libraries you need.
24.	Change to the correct sub-directory (efis_to_hud) by typing “cd efis_to_hud”
1.	then to run the script type   ./setup.sh
2.	It will take several minutes to complete the setup
3.	Next Reboot the PI. Enter:  reboot
25.	To input/playback (from separate PC)  External Recorded HUD Data start data playback into Serial-TTL Converter
26.	Next run the “serial_read.py” script to confirm correct data is being sent to the PI 
1.	Change directory back to “efis_to_hud”  dir then type Enter:  cd efis_to_hud
27.	Enter:  python serial_read.py
28.	Make sure the data is coming through and looks good.
29.	To exit enter cntrl-c
30.	To Run current HUD program enter “sudo python hud.py” (arguments as shown below will appear).

 
Note: You have to run using sudo in order to get access to serial port.

 

## Some Graphics Pointers

Note doe our developers: perhaps you could do a write up as you learn how to using the drawing functions.  So we can publish it in a HowTo and others can learn from it.


PyGame is a module for python that is made for doing graphics for games.  But turns out that it’s good for doing graphics for other things too.  There is a Init sequence that is already handled by the hud.py and hud_graphics.py scripts.  So the custom screens don’t have to do much for that.  But the 2 main functions that get called are…

`
def initDisplay (self, pygamescreen, width, height): 
`

This gets called once when the screen loads.  It creates objects and vars that only need to be created once on startup of the screen.

a good example is loading fonts.  We only need to load them once.  The following example shows us loading a monospace font at point 40 and calling it fontIndicator so we can use it later in the draw function.

`
self.fontIndicator = pygame.font.SysFont("monospace", 40)  # ie IAS and ALT
def clearScreen(self):
`

This is called before every redraw of the screen.  To set the screen to the default color you want..  most likely black.  which is (0, 0, 0)  each number is a color value.  (Red, Green, Blue)

`
def draw(self, aircraft):
`

This gets called every redraw cycle.  Which depending on how fast the pi is can be around 15 to 20 times a sec. 

hud_graphics.hud_draw_horz_lines is a helpful function I created so all screens can use it to draw the hud lines.


The following is how we draw text to the screen.

`label = self.myfont.render("Pitch: %d" % (aircraft.pitch), 1, (255, 255, 0))
self.pygamescreen.blit(label, (0, 0))`

the myfont.render is rendering the text and color (Red,Green,Blue) of 255,255,0.   The myfont was loaded back in the initDisplay function.
then the next line does a “blit” which is what term used when you copy it to the graphics buffer to show on the screen.  In this case at position x=0, y=0


hud_graphics.hud_draw_box_text(  is a util function I created, again to help people to do common drawing tasks.  like drawing text with a box around it.  You can see these helpful functions in the hud_graphics.py file.

pygame.draw.circle  is used for drawing a circle.


Here is a list of other nice drawing functions.  https://www.pygame.org/docs/ref/draw.html

You can google around on using pygame to draw things and probably find lots of examples.

`def processEvent(self, event):`

This is used to process key commands to make your hud screen do different things.

If you create useful functions for drawing things that others might want to use, then it would be nice to put that into a separate file.

 


## Raspberry Pi Zero Wiring
 
Python Programming Language: has many similarities to Perl, C, and Java. However, there are some definite differences between the languages.


Python Tutorial https://www.tutorialspoint.com/python/index.htm


Python Beginner Cheat Sheet https://github.com/ehmatthes/pcc/.../v1.../beginners_python_cheat_sheet_pcc_all.pdf
 


## Basic Raspian OS Commands

```
Filesystem
Ls     The ls command lists the content of the current directory (or one that is specified). It can be used with the -l flag to display additional information (permissions, owner, group, size, date and timestamp of last edit) about each file and directory in a list format. The -a flag allows you to view files beginning with  . (i.e. dotfiles).
cd     Using cd changes the current directory to the one specified. You can use relative (i.e. cd directoryA) or absolute (i.e. cd /home/pi/directoryA) paths.
pwd     The pwd command displays the name of the present working directory: on a Raspberry Pi, entering pwd will output something like /home/pi.
mkdir     You can use mkdir to create a new directory, e.g. mkdir newDir would create the directory newDir in the present working directory.
rmdir     To remove empty directories, use rmdir. So, for example, rmdir oldDir will remove the directory oldDir only if it is empty.
rm     The command rm removes the specified file (or recursively from a directory when used with -r). Be careful with this command: files deleted in this way are mostly gone for good!
cp     Using cp makes a copy of a file and places it at the specified location (this is similar to copying and pasting). For example, cp ~/fileA /home/otherUser/ would copy the file fileA from your home directory to that of the user  otherUser (assuming you have permission to copy it there). This command can either take FILE FILE (cp fileA fileB), FILE DIR (cp fileA /directoryB/) or -r DIR DIR (which recursively copies the contents of directories) as arguments.
mv     The mv command moves a file and places it at the specified location (so where  cp performs a 'copy-paste', mv performs a 'cut-paste'). The usage is similar to  cp. So mv ~/fileA /home/otherUser/ would move the file fileA from your home directory to that of the user otherUser. This command can either take  FILE FILE (mv fileA fileB), FILE DIR (mv fileA /directoryB/) or  DIR DIR (mv /directoryB /directoryC) as arguments. This command is also useful as a method to rename files and directories after they've been created.
touch     The command touch sets the last modified time-stamp of the specified file(s) or creates it if it does not already exist.
cat     You can use cat to list the contents of file(s), e.g. cat thisFile will display the contents of thisFile. Can be used to list the contents of multiple files, i.e.  cat *.txt will list the contents of all .txt files in the current directory.
head     The head command displays the beginning of a file. Can be used with -n to specify the number of lines to show (by default ten), or with -c to specify the number of bytes.
tail     The opposite of head, tail displays the end of a file. The starting point in the file can be specified either through -b for 512 byte blocks, -c for bytes, or  -n for number of lines.
chmod     You would normally use chmod to change the permissions for a file. The chmod command can use symbols u (user that owns the file), g (the files group) , and  o (other users) and the permissions r (read), w (write), and x (execute). Using chmod u+x *filename* will add execute permission for the owner of the file.
chown     The chown command changes the user and/or group that owns a file. It normally needs to be run as root using sudo e.g. sudo chown pi:root *filename* will change the owner to pi and the group to root.
ssh     ssh denotes the secure shell. Connect to another computer using an encrypted network connection. For more details see SSH (secure shell)
scp     The scp command copies a file from one computer to another using ssh. For more details see SCP (secure copy)
sudo     The sudo command enables you to run a command as a superuser, or another user. Use sudo -s for a superuser shell. For more details see Root user / sudo
dd     The dd command copies a file converting the file as specified. It is often used to copy an entire disk to a single file or back again. So, for example,  dd if=/dev/sdd of=backup.img will create a backup image from an SD card or USB disk drive at /dev/sdd. Make sure to use the correct drive when copying an image to the SD card as it can overwrite the entire disk.
df     Use df to display the disk space available and used on the mounted filesystems. Use df -h to see the output in a human-readable format using M for MBs rather than showing number of bytes.
unzip     The unzip command extracts the files from a compressed zip file.
tar     Use tar to store or extract files from a tape archive file. It can also reduce the space required by compressing the file similar to a zip file.  
To create a compressed file, use  tar -cvzf *filename.tar.gz* *directory/* To extract the contents of a file, use tar -xvzf *filename.tar.gz*
pipes     A pipe allows the output from one command to be used as the input for another command. The pipe symbol is a vertical line |. For example, to only show the first ten entries of the ls command it can be piped through the head command  ls | head
tree     Use the tree command to show a directory and all subdirectories and files indented as a tree structure.
&     Run a command in the background with &, freeing up the shell for future commands.
wget     Download a file from the web directly to the computer with wget. So  wget https://www.raspberrypi.org/documentation/linux/usage/commands.md will download this file to your computer as commands.md
curl     Use curl to download or upload a file to/from a server. By default, it will output the file contents of the file to the screen.
man     Show the manual page for a file with man. To find out more, run man man to view the manual page of the man command.
Search
grep     Use grep to search inside files for certain search patterns. For example,  grep "search" *.txt will look in all the files in the current directory ending with .txt for the string search.
The grep command supports regular expressions which allows special letter combinations to be included in the search.
awk     awk is a programming language useful for searching and manipulating text files.
find     The find command searches a directory and subdirectories for files matching certain patterns.
whereis     Use whereis to find the location of a command. It looks through standard program locations until it finds the requested command.
Networking
ping     The ping utility is usually used to check if communication can be made with another host. It can be used with default settings by just specifying a hostname (e.g. ping raspberrypi.org) or an IP address (e.g. ping 8.8.8.8). It can specify the number of packets to send with the -c flag.
nmap     nmap is a network exploration and scanning tool. It can return port and OS information about a host or a range of hosts. Running just nmap will display the options available as well as example usage.
hostname     The hostname command displays the current hostname of the system. A privileged (super) user can set the hostname to a new one by supplying it as an argument (e.g. hostname new-host).
ifconfig     Use ifconfig to display the network configuration details for the interfaces on the current system when run without any arguments (i.e. ifconfig). By supplying the command with the name of an interface (e.g. eth0 or lo) you can then alter the configuration: check the manual page for more details.

```
