#!/bin/python3

import socket, sys, pifacecad, time, re
from telnetlib import Telnet
from urllib import parse

configFile='/etc/default/squeezelite'
PlayerID=''
PlayerIDEnc=''
mode = 0
play, songlen, backlight = 0,0,0
volume = "20"
delay=0.5
dispIlock=0
title=""

# Check and display 
def write_to_cad(text):
    global cad, delay
    global dispIlock
    while (dispIlock==1):
        #print('Interlock.')
        sleep(.1)

    dispIlock=1
    #print(text)
    #pos=re.match('[A-Z0-9\ !"£$%^&\*()-_+=#@:.,?\{\}]',text)
    #print(str(pos))
    cad.lcd.write(text)
    time.sleep(delay)
    dispIlock=0


# Define and store custom bitmaps to be displayed
def custom_bitmaps():
	speaker = pifacecad.LCDBitmap([1,3,15,15,15,3,1,0])
	back = pifacecad.LCDBitmap([0,2,6,14,6,2,0,0])
	play = pifacecad.LCDBitmap([0,8,12,14,12,8,0,0])
	stop = pifacecad.LCDBitmap([0,31,31,31,31,31,0,0])
	pause = pifacecad.LCDBitmap([0,27,27,27,27,27,0,0])
	playlist = pifacecad.LCDBitmap([2,3,2,2,14,30,12,0])
	
	cad.lcd.store_custom_bitmap(0, speaker)
	cad.lcd.store_custom_bitmap(1, play)
	cad.lcd.store_custom_bitmap(2, stop)
	cad.lcd.store_custom_bitmap(3, pause)
	cad.lcd.store_custom_bitmap(4, playlist)
	cad.lcd.store_custom_bitmap(5, back)


def display_volume(avolume):
        global volume
        # Keep a copy for mode switches...
        volume=avolume
        if (volume=="00"):
            volume="100"
        cad.lcd.set_cursor(12,1)
        #cad.lcd.write(avolume)
        write_to_cad(volume+'% ')
        #cad.lcd.write('% ')
        #print(avolume)

# Display the play or pause icon
def display_play(play):
        global dispIlock
        while (dispIlock==1):
            #print('Interlock.')
            sleep(.1)

        dispIlock=1
        cad.lcd.set_cursor(0,1)
        if (play==0):
           cad.lcd.write_custom_bitmap(3)
        else:
           cad.lcd.write_custom_bitmap(1)

        time.sleep(delay)
        dispIlock=0

# Send the seek request
def seek_forward(step):
        # Send the request
        #telnet.write('seek forward')
        #for now, just say something
        cad.lcd.set_cursor(13,1)
        #cad.lcd.write(str(step))
        write_to_cad(str(step))

# Init display by showing idle state    
def init_display():
        cad.lcd.blink_off()
        cad.lcd.cursor_off()
        cad.lcd.clear()
        write_to_cad(title)
        cad.lcd.set_cursor(11, 1)
        cad.lcd.write_custom_bitmap(0)
        display_volume(volume)
 

# Handle the button presses
def update_pin_text(event):
  event.chip.lcd.set_cursor(0,0)
  global mode, volume
  global conn, cad
  global PlayerID

  if (event.pin_num == 0):
      msg=PlayerID+' pause'
      conn.write(msg.encode('ascii')+b"\n")

  elif (event.pin_num == 1):
      msg=PlayerID+' playlist jump -1'
      conn.write(msg.encode('ascii')+b"\n")

  elif (event.pin_num == 2):
      msg=PlayerID+' playlist jump +1'
      conn.write(msg.encode('ascii')+b"\n")

  elif (event.pin_num == 3):
      cad.init_board() 
      init_display() 
      #event.chip.lcd.clear()

  elif (event.pin_num == 4):
     global backlight
     if (backlight == 0):
        event.chip.lcd.backlight_on()
        backlight = 1
     else:
        event.chip.lcd.backlight_off()
        backlight = 0

  elif (event.pin_num == 7):
     if (mode == 0):
        msg=PlayerID+' mixer volume +5'
        conn.write(msg.encode('ascii')+b"\n")
     else:
        msg=PlayerID+' time 30'
        conn.write(msg.encode('ascii')+b"\n")

  elif (event.pin_num == 6):
     if (mode == 0):
        msg=PlayerID+' mixer volume -5'
        conn.write(msg.encode('ascii')+b"\n")
     else:
        msg=PlayerID+' time -30'
        conn.write(msg.encode('ascii')+b"\n")

  elif (event.pin_num == 5):
     if (mode == 0):
        cad.lcd.set_cursor(11,1)
        cad.lcd.write_custom_bitmap(5)
        cad.lcd.write_custom_bitmap(1)
        write_to_cad("   ")
        time.sleep(delay)
        mode = 1
     else:
        cad.lcd.set_cursor(11,1)
        cad.lcd.write_custom_bitmap(0)
        time.sleep(delay)
        mode = 0
        display_volume(volume)



def ReadConfig():
  f = open (configFile, 'r')
  for line in f:
    if line.find('SLMAC') == 0:
      MAC=line.find(':')-2
      END=line.find('"', MAC)
      Full=line[MAC:END]

  #print(Full)
  Full2=parse.quote(Full)
  #print(Full2)

  f.close
  return Full


def displayline(line):
  global cad, mode, songlen, title

  if line.find('newsong') >0:
     oldlen=songlen
     cad.lcd.set_cursor(0,0)
     pos=line.find('newsong')
     pos=line.find(' ', pos+6)
     song=line[pos+1:-2]
     if (song != title):
         songlen=len(line)-pos-3
         write_to_cad(song[:80])
         title=song
     if (songlen < oldlen):
        songadd="                                                                                 "[songlen-oldlen:]
        write_to_cad(songadd)

  elif (line.find('playlist pause 0')>0):
     display_play(1)

  elif (line.find('playlist pause 1')>0):
     display_play(0)

  elif (line.find('server volume')>0) and (mode==0):
     display_volume(line[-2:])

  elif (line.find('status ')>0):
      pos=line.find('mode:')
      if (line.find('play', pos) == pos+5):
          display_play(1)
      else:
          display_play(0)

      pos=line.find('volume:')
      pos2=line.find(' ',pos)
      volume=line[pos+7:pos2]
      display_volume(volume)          

  elif (line.find('title ')>0): 
     oldlen=songlen
     cad.lcd.set_cursor(0,0)
     pos=line.find('title ')
     pos=line.find(' ', pos+4)
     song=line[pos+1:]
     if (song != title):
         songlen=len(line)-pos-3
         write_to_cad(song[:80])
         title=song
     if (songlen < oldlen):
        songadd="                                                                                 "[songlen-oldlen:]
        write_to_cad(songadd)

  
  #Pause to let the PF Cad catchup - maybe
  time.sleep(delay)



# Main loop
cad = pifacecad.PiFaceCAD()

#cad.lcd.write("OK")

custom_bitmaps()
init_display()
listener = pifacecad.SwitchEventListener(chip=cad)

for i in range(8):
  listener.register(i, pifacecad.IODIR_RISING_EDGE, update_pin_text)
listener.activate()

PlayerID=ReadConfig()
PlayerIDEnc=parse.quote(PlayerID)
#print (PlayerID)
#print (PlayerIDEnc)
conn=Telnet('192.168.144.8', 9090)
conn.open('192.168.144.8', 9090)

fullLine=""

#list="players name"
list=PlayerID+' status'
conn.write(list.encode('ascii')+b"\n")
list="subscribe prefset,playlist"
conn.write(list.encode('ascii')+b"\n")
list=PlayerID+' title ?'
conn.write(list.encode('ascii')+b"\n")
while 1:
  try:
    readline=conn.read_eager()
  except:
    sys.exit()

  if (len(readline) >0 ):
     LineEnd=readline.find(b'\n')
     if LineEnd == -1:
       fullLine+=readline.decode('utf8')

     if LineEnd == 0:
       fullLine=parse.unquote(fullLine)
       #print (fullLine)
       displayline(fullLine)
       readline=readline[2:len(readline)]
       fullLine=readline.decode('utf8')

     if LineEnd > 0:
       line=readline[0:LineEnd]
       fullLine+=line.decode('utf-8')
       fullLine=parse.unquote(fullLine)
       #if fullLine.find(Full2) == 0:
       #print (fullLine)
       displayline(fullLine)
       line=readline[LineEnd+1:len(readline)]
       fullLine=line.decode('utf-8')

  #else:
  #time.sleep(delay)  


