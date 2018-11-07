#!/usr/bin/env python

import math, os, sys, random
import argparse, pygame
import time
import serial
import struct
import threading, getopt
import ConfigParser


def readConfig(section,name,defaultValue=0,show_error=False):
    global configParser
    try:
        value = configParser.get(section, name)
        return value
    except Exception as e:
        if show_error == True:
            print "config error section: ",section," key:",name," -- not found"
        return defaultValue
    else:
        return defaultValue

def readConfigInt(section,name,defaultValue=0):
    return int(readConfig(section,name,defaultValue=defaultValue))

class Vehicle(object):
    def __init__(self, data_source="random", network_source=None):
        self.data_source = data_source
        self.network_source = network_source
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.alt = 0
        self.airspeed = 0

        if self.data_source == "network":
            if not self.network_source:
                raise TypeError

            import requests
            self.network_source['requests_session'] = requests.Session()

    def get_orientation(self):
        global efis_roll
        global efis_pitch
        self.set_orientation(roll=efis_roll, pitch=efis_pitch)
        return {'roll':     self.roll,
                'pitch':    self.pitch,
                'yaw':      self.yaw,
                'alt':      self.alt,
                'airspeed': self.airspeed}

    def set_orientation(self, roll=None, pitch=None, yaw=None, alt=None, airspeed=None):
        if roll != None:
            self.roll = roll

        if pitch != None:
            self.pitch = pitch

        if yaw != None:
            self.yaw = yaw

        if alt != None:
            self.alt = alt

        if airspeed != None:
            self.airspeed = airspeed

def debug_print(debug, string, level=1):
    if debug >= level:
        print string

def display_init(debug):
    pygame.init()
    disp_no = os.getenv('DISPLAY')
    if disp_no:
    #if False:
        debug_print(debug, "I'm running under X display = {0}".format(disp_no))
        size = 640, 480
        #size = 320, 240
        screen = pygame.display.set_mode(size)
    else:
        drivers = ['directfb', 'fbcon', 'svgalib']
        found = False
        for driver in drivers:
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)

            try:
                pygame.display.init()
            except pygame.error:
                debug_print(debug, 'Driver: {0} failed.'.format(driver))
                continue

            found = True
            break

        if not found:
            raise Exception('No suitable video driver found!')

        size = pygame.display.Info().current_w, pygame.display.Info().current_h
        screen = pygame.display.set_mode(size, pygame.FULLSCREEN)

    return screen, size

def generateHudReferenceLine(screen_width, screen_height, ahrs_center, pitch=0, roll=0, deg_ref=0,line_mode=1):

    if line_mode == 1:
        if deg_ref == 0:
            length = screen_width*.9
        elif (deg_ref%10) == 0:
           length = screen_width*.2
        elif (deg_ref%5) == 0:
           length = screen_width*.1
    else:
        if deg_ref == 0:
            length = screen_width*.6
        elif (deg_ref%10) == 0:
           length = screen_width*.1
        elif (deg_ref%5) == 0:
           length = screen_width*.05

    ahrs_center_x, ahrs_center_y = ahrs_center
    px_per_deg_y = screen_height / 60
    pitch_offset = px_per_deg_y * (-pitch + deg_ref)

    center_x = ahrs_center_x - (pitch_offset * math.cos(math.radians(90 - roll)))
    center_y = ahrs_center_y - (pitch_offset * math.sin(math.radians(90 - roll)))

    x_len = length * math.cos(math.radians(roll))
    y_len = length * math.sin(math.radians(roll))

    start_x = center_x - (x_len / 2)
    end_x = center_x + (x_len / 2)
    start_y = center_y + (y_len / 2)
    end_y = center_y - (y_len / 2)

    return [[start_x, start_y], [end_x, end_y]]

def read_all(port, chunk_size=200):
    """Read all characters on the serial port and return them."""
    if not port.timeout:
        raise TypeError('Port needs to have a timeout set!')

    read_buffer = b''

    while True:
        # Read in chunks. Each chunk will wait as long as specified by
        # timeout. Increase chunk_size to fail quicker
        byte_chunk = port.read(size=chunk_size)
        read_buffer += byte_chunk
        if not len(byte_chunk) == chunk_size:
            break

    return read_buffer

def readSerial(num):
    global ser
    if (ser.inWaiting()>0):
        t = ser.read(1)

def readMGLMessage():
  global ser
  global efis_pitch, efis_roll, efis_ias , efis_pres_alt, efis_aoa,efis_mag_head
  try:
    x = 0
    while x != 5:
      t = ser.read(1)
      if len(t) != 0:
        x = ord(t);
    stx = ord(ser.read(1))
    
    if stx == 2:
      MessageHeader = ser.read(6)
      if(len(MessageHeader) == 6):
        msgLength,msgLengthXOR,msgType,msgRate,msgCount,msgVerion = struct.unpack("!BBBBBB", MessageHeader)

        if msgType == 3 : # attitude information
            Message = ser.read(25)
            if(len(Message) == 25):
                # use struct to unpack binary data.  https://docs.python.org/2.7/library/struct.html
                HeadingMag,PitchAngle,BankAngle,YawAngle,TurnRate,Slip,GForce,LRForce,FRForce,BankRate,PitchRate,YawRate,SensorFlags = struct.unpack("<HhhhhhhhhhhhB", Message)
                efis_pitch = PitchAngle * 0.1 # should this be * 0.1
                efis_roll = BankAngle * 0.1 # should this be * 0.1
                efis_mag_head = HeadingMag * 0.1
                ser.flushInput()

        if msgType == 1 : # Primary flight
            Message = ser.read(18)
            if(len(Message) == 18):
                PAltitude,BAltitude,ASI,TAS,AOA,VSI,Baro = struct.unpack("<iiHHhhH", Message)
                if ASI>0:
                    efis_ias = ASI * 0.05399565
                efis_pres_alt = PAltitude
                efis_aoa = AOA

        if msgType == 6 : # Traffic message
            Message = ser.read(4)
            if(len(Message) == 4):
                TrafficMode,NumOfTraffic,NumMsg,MsgNum = struct.unpack("!BBBB", Message)

        if msgType == 4 : # Navigation message
            Message = ser.read(24)
            if(len(Message) == 24):
                Flags,HSISource,VNAVSource,APMode,Padding,HSINeedleAngle,HSIRoseHeading,HSIDeviation,VerticalDeviation,HeadingBug,AltimeterBug,WPDistance = struct.unpack("<HBBBBhHhhhii", Message)

    else:
      return
  except serial.serialutil.SerialException:
    print "exception"

def readSkyviewMessage():
  global ser
  global efis_pitch, efis_roll, efis_ias, efis_pres_alt, efis_aoa,efis_mag_head
  try:
    x = 0
    while x != 33:  # 33(!) is start of dynon skyview.
      t = ser.read(1)
      if len(t) != 0:
        x = ord(t)
    msg = ser.read(91)
    if len(msg) == 91:
      msg = (msg[:73]) if len(msg) > 73 else msg
      dataType,DataVer,SysTime,pitch,roll,HeadingMAG,IAS,PresAlt,TurnRate,LatAccel,VertAccel,AOA,VertSpd,OAT,TAS,Baro,DA,WD,WS,Checksum,CRLF = struct.unpack("cc8s4s5s3s4s6s4s3s3s2s4s3s4s3s6s3s2s2s2s", msg)
      if ord(CRLF[0]) == 13:
        if dataType == '1':
            efis_roll = int(roll) * 0.1
            efis_pitch = int(pitch) * 0.1
            efis_ias = int(IAS) * 0.1
            efis_pres_alt = int(PresAlt)
            efis_aoa = int(AOA)
            efis_mag_head = int(HeadingMAG)
            ser.flushInput()

    else:
      ser.flushInput()
      return
  except serial.serialutil.SerialException:
    print "exception"


class Point:
    # constructed using a normal tupple
    def __init__(self, point_t = (0,0)):
        self.x = float(point_t[0])
        self.y = float(point_t[1])
    # define all useful operators
    def __add__(self, other):
        return Point((self.x + other.x, self.y + other.y))
    def __sub__(self, other):
        return Point((self.x - other.x, self.y - other.y))
    def __mul__(self, scalar):
        return Point((self.x*scalar, self.y*scalar))
    def __div__(self, scalar):
        return Point((self.x/scalar, self.y/scalar))
    def __len__(self):
        return int(math.sqrt(self.x**2 + self.y**2))
    # get back values in original tuple format
    def get(self):
        return (self.x, self.y)

def draw_dashed_line(surf, color, start_pos, end_pos, width=1, dash_length=10):
    origin = Point(start_pos)
    target = Point(end_pos)
    displacement = target - origin
    length = len(displacement)
    slope = displacement/length

    for index in range(0, length/dash_length, 2):
        start = origin + (slope *    index    * dash_length)
        end   = origin + (slope * (index + 1) * dash_length)
        pygame.draw.line(surf, color, start.get(), end.get(), width)


def main():
    global done, efis_pitch, efis_roll, efis_ias, efis_pres_alt, efis_aoa,efis_mag_head
    ahrs_line_deg = readConfigInt('HUD','vertical_degrees',15)
    print "ahrs_line_deg = ", ahrs_line_deg;

    maxframerate = 20
    screen, screen_size = display_init(0)
    width, height = screen_size
    pygame.mouse.set_visible(False)

    WHITE = (0, 255, 0)
    BLACK = (0, 0, 0)

    font = pygame.font.SysFont(None, int(height/20))

    #v = Vehicle(data_source=args.datasource, network_source={'host': args.networkhost})
    v = Vehicle()

    ahrs_bg = pygame.Surface((width*2, height*2))
    ahrs = ahrs_bg
    ahrs_bg_width = ahrs_bg.get_width()
    ahrs_bg_height = ahrs_bg.get_height()
    ahrs_bg_center = (ahrs_bg_width/2, ahrs_bg_height/2)

    clock = pygame.time.Clock()
    myfont = pygame.font.SysFont("monospace", 22) # initialize font; must be called after 'pygame.init()' to avoid 'Font not Initialized' error
    show_debug = False
    line_mode = 1
    alt_box_mode = 0
    line_thickness = 2
    center_circle_mode = 0

    while not done:
        clock.tick(maxframerate)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                thread1.stop()
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    done = True
                if event.key == pygame.K_d:
                    show_debug = not show_debug
                if event.key == pygame.K_EQUALS:
                    #height = height + 10
                    width = width + 10
                if event.key == pygame.K_MINUS:
                    #height = height - 10
                    width = width - 10
                if event.key == pygame.K_SPACE:
                    line_mode = not line_mode
                if event.key == pygame.K_a:
                    alt_box_mode = not alt_box_mode
                if event.key == pygame.K_l:
                    line_thickness += 1
                    if line_thickness > 8: line_thickness = 2
                if event.key == pygame.K_c:
                    center_circle_mode += 1
                    if center_circle_mode > 3: center_circle_mode = 0

        o = v.get_orientation()
        roll = o['roll']
        pitch = o['pitch']

        #debug_print(args.debug, "Roll:  {:.1f}".format(roll))
        #debug_print(args.debug, "Pitch: {:.1f}".format(pitch))
        #debug_print(args.debug, "")

        ahrs.fill(BLACK)

        # range isn't inclusive of the stop value, so if stop is 60 then there's no line make
        # for 60
        for l in range(-60, 61, ahrs_line_deg):
            line_coords = generateHudReferenceLine(width, height, ahrs_bg_center, pitch=pitch, roll=roll, deg_ref=l, line_mode=line_mode)

            if abs(l)>45:
                if l%5 == 0 and l%10 != 0:
                    continue

            #debug_print(args.debug, "Deg: {0}".format(l), 2)
            #debug_print(args.debug, "Line Coords: {0}".format(line_coords), 2)
            #debug_print(args.debug, "", 2)
            if(l<0):
                draw_dashed_line(ahrs_bg, WHITE, line_coords[0], line_coords[1], width=line_thickness, dash_length=5)
            else:
                pygame.draw.lines(ahrs_bg, WHITE, False, line_coords, line_thickness)

            # render debug text
            #if show_debug:
            #    label = myfont.render("Deg: %d Line Coord %d" % (l,line_coords), 1, (255,255,0))
            #    screen.blit(label, (ahrs.get_width()-100, 0))

            # draw degree text
            if l != 0 and l%10 == 0:
                text = font.render(str(l), False, WHITE)
                text_width, text_height = text.get_size()
                left = int(line_coords[0][0]) - (text_width + int(width/100))
                top = int(line_coords[0][1]) - text_height / 2
                ahrs_bg.blit(text, (left, top))

        top_left = (-(ahrs.get_width() - width)/2, -(ahrs.get_height() - height)/2)
        screen.blit(ahrs, top_left)

        # render debug text
        if show_debug:
            label = myfont.render("Pitch: %d" % (pitch), 1, (255,255,0))
            screen.blit(label, (0, 0))
            label = myfont.render("Roll: %d" % (roll), 1, (255,255,0))
            screen.blit(label, (0, 20))
            label = myfont.render("IAS: %d" % (efis_ias), 1, (255,255,0))
            screen.blit(label, (0, 40))
            label = myfont.render("PresAlt: %d" % (efis_pres_alt), 1, (255,255,0))
            screen.blit(label, (0, 60))
            label = myfont.render("AOA: %d" % (efis_aoa), 1, (255,255,0))
            screen.blit(label, (0, 80))
            label = myfont.render("MagHead: %d" % (efis_mag_head), 1, (255,255,0))
            screen.blit(label, (0, 100))

        #pygame.draw.lines(screen, WHITE, False, [[0, height/2], [10, height/2]], 2)
        #pygame.draw.lines(screen, WHITE, False, [[width-10, height/2], [width, height/2]], 2)
        if alt_box_mode:
            pygame.draw.rect(screen,WHITE,(0,height/4,100,height/1.5),1)
            pygame.draw.rect(screen,WHITE,(width-100,height/4,100,height/1.5),1)

        if center_circle_mode == 0:
            pygame.draw.circle(screen, WHITE, (width/2,height/2), 15, 1)
        if center_circle_mode == 1:
            pygame.draw.circle(screen, WHITE, (width/2,height/2), 3, 1)
        if center_circle_mode == 2:
            pygame.draw.circle(screen, WHITE, (width/2,height/2), 50, 1)


        pygame.display.flip()

    pygame.quit()
    os.system('killall python')

class myThreadSerialReader (threading.Thread):
   def __init__(self):
      threading.Thread.__init__(self)
   def run(self):
        global done
        if efis_data_format == 'skyview':
          while 1 and done==False:
            readSkyviewMessage()
        elif efis_data_format == 'mgl':
          while 1 and done==False:
            readMGLMessage()
        else:
            done = True
            print "Unkown efis_data_format: ",efis_data_format
        pygame.quit()
        sys.exit()


def showArgs():
  global efis_data_format
  print 'hud.py <options>'
  print ' -m (MGL iEFIS)'
  print ' -s (Dynon Skyview)'
  if os.path.isfile("hud.cfg") == False:
    print ' hud.cfg not found (default values will be used)'
  else:
    print ' hud.cfg FOUND'
    print ' hud.cfg efis_data_format=',efis_data_format

  sys.exit()


# open serial connection.
ser = serial.Serial(  
  port='/dev/ttyS0',
  baudrate = 115200,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
)
configParser = ConfigParser.RawConfigParser()   
configParser.read("hud.cfg")

efis_pitch = 0.1
efis_roll = 0.1
efis_ias = 0
efis_pres_alt = 0
efis_mag_head = 0
done = False

if __name__ == '__main__':
    argv = sys.argv[1:]
    efis_data_format = readConfig("HUD","efis_data_format","none")
    try:
      opts, args = getopt.getopt(argv,'hsm', ['skyview=',])
    except getopt.GetoptError:
      showArgs()
    for opt, arg in opts:
      if opt == '-h':
        showArgs()
      elif opt == '-s':
        efis_data_format = 'skyview'
      elif opt == '-m':
        efis_data_format = 'mgl'
    if efis_data_format == 'none': showArgs()

    thread1 = myThreadSerialReader()
    thread1.start()
   
    sys.exit(main())

# vi: modeline tabstop=8 expandtab shiftwidth=4 softtabstop=4 syntax=python
