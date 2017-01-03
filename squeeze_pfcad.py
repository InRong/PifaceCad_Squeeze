#!/bin/python3

import socket, sys, pifacecad, time, re
from telnetlib import Telnet
from urllib import parse

configFile='/etc/default/squeezelite'
PlayerID=''
PlayerIDEnc=''
mode = 0
loop = 0
rescnt = 0
play, songlen, backlight = 0,0,0
volume = "20"
slider, mult=0, 5
delay=0.05
dispIlock=0
title=""
titleDispLen=16
DisplayPos, MoveTime, MoveRate=0,0,10
global conn

# Check and display 
def write_to_cad(text):
    global cad, delay
    #print (text)
    while (len(text) > 0):
        cad.lcd.write(text[:4])
        text=text[4:]

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


def display_pos(songpos):
    global mode
    if (mode==1):
        full=songpos+'   '
        #pos=strtoint(songpos)
        #full=str(pos // 60)+':'+str(pos % 60)+'   '
        cad.lcd.set_cursor(11,1)
        write_to_cad(full)


def display_volume(avolume):
        global volume, mode
        if (volume!=avolume) and (mode==0):
            volume=avolume
            if (volume=="00"):
                volume="100"
    
            if (volume=="5"):
                volume=" 5"
    
            cad.lcd.set_cursor(10,1)
            #cad.lcd.write(avolume)
            write_to_cad(volume+'% ')
            #cad.lcd.write('% ')
            #print(avolume)

# Display the play or pause icon
def display_play(Newplay):
        global play
        play=Newplay
        cad.lcd.set_cursor(0,1)
        if (play==0):
           cad.lcd.write_custom_bitmap(3)
        else:
           cad.lcd.write_custom_bitmap(1)

        time.sleep(delay)

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
        #write_to_cad(title)
        cad.lcd.set_cursor(11, 1)
        #time.sleep(delay)
        cad.lcd.write_custom_bitmap(0)
        #time.sleep(delay)
        display_volume(volume)
        #time.sleep(delay)
        display_play(play)
 

# Handle the button presses
#def update_pin_text(event):
#  event.chip.lcd.set_cursor(0,0)
#  global mode, volume
#  global conn, cad
#  global PlayerID

#  if (event.pin_num == 0):
def pushed_play(event):      
      global conn
      msg=PlayerID+' pause'
      conn.write(msg.encode('ascii')+b"\n")

#  elif (event.pin_num == 1):
def pushed_back(event):
      global conn
      msg=PlayerID+' playlist jump -1'
      conn.write(msg.encode('ascii')+b"\n")

#  elif (event.pin_num == 2):
def pushed_forward(event):
      global conn
      msg=PlayerID+' playlist jump +1'
      conn.write(msg.encode('ascii')+b"\n")

#  elif (event.pin_num == 3):
def reset(event):
      global rescnt, title, volume
      cad.init_board() 
      init_display() 
      #event.chip.lcd.clear()
      #display_volume(volume)
      volume=""
      title=""
      rescnt+=1
      #print(str(rescnt))

def clear(event):
    #global mode
    global mode
    init_display()
    # Use the set mode to help reset the display, so toggle in readyness for the retoggle
    if (mode==0):
        mode=1
    else:
        mode=0

    time.sleep(delay)
    slider_in(event)
    list=PlayerID+' title ?'
    time.sleep(delay)
    conn.write(list.encode('ascii')+b"\n")


#  elif (event.pin_num == 4):
def pushed_blight(event):
     global backlight
     if (backlight == 0):
        event.chip.lcd.backlight_on()
        backlight = 1
     else:
        event.chip.lcd.backlight_off()
        backlight = 0

#  elif (event.pin_num == 7):
def slider_right(event):
    global slider
    slider+=1
     #if (mode == 0):
        #msg=PlayerID+' mixer volume +5'
        #conn.write(msg.encode('ascii')+b"\n")
     #else:
     #   msg=PlayerID+' time 30'
     #   conn.write(msg.encode('ascii')+b"\n")

#  elif (event.pin_num == 6):
def slider_left(event):
    global slider
    slider-=1
#     if (mode == 0):
#        msg=PlayerID+' mixer volume -5'
#        conn.write(msg.encode('ascii')+b"\n")
#     else:
#        msg=PlayerID+' time -30'
#        conn.write(msg.encode('ascii')+b"\n")

#  elif (event.pin_num == 5):
def slider_in(event):
     global slider, mult, mode #, volume
     slider=0
     if (mode == 0):
        cad.lcd.set_cursor(9,1)
        cad.lcd.write_custom_bitmap(5)
        time.sleep(delay)
        cad.lcd.write_custom_bitmap(1)
        time.sleep(0.3)
        write_to_cad("   ")
        mode = 1
        mult=30
     else:
        cad.lcd.set_cursor(9,1)
        cad.lcd.write_custom_bitmap(0)
        time.sleep(delay)
        mode = 0
        display_volume('  ')
        mult=5


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

  #print(line)
  #if line.find('newsong') >0:
  #   oldlen=songlen
  #   cad.lcd.set_cursor(0,0)
  #   pos=line.find('newsong')
  #   pos=line.find(' ', pos+6)
  #   song=line[pos+1:-2]
  #   if (song != title):
  #       songlen=len(line)-pos-3
  #       write_to_cad(song[:80])
  #       title=song
  #   if (songlen < oldlen):
  #      songadd="                                                                                 "[songlen-oldlen:]
  #      write_to_cad(songadd)

  #elif (line.find('playlist pause 0')>0):
  #   display_play(1)

  #elif (line.find('playlist pause 1')>0):
  #   display_play(0)

  #elif (line.find('server volume')>0) and (mode==0):
  #   display_volume(line[-2:])

  #elif (line.find('status ')>0):
  if (line.find('status ')>0):
      pos=line.find('mode:')
      if (line.find('play', pos) == pos+5):
          display_play(1)
      else:
          display_play(0)

      pos=line.find('volume:')
      pos2=line.find(' ',pos)
      volume=line[pos+7:pos2]
      display_volume(volume)          
      pos=line.find('time:')
      pos2=line.find('.',pos)
      songpos=line[pos+5:pos2]
      display_pos(songpos)

  elif (line.find('title ')>0): 
     oldlen=songlen
     cad.lcd.set_cursor(0,0)
     pos=line.find('title ')
     pos=line.find(' ', pos+4)
     if (pos > 0):
       song=line[pos+1:]
       if (song != title):
         #songlen=len(line)-pos-3
         songlen=len(song)
         write_to_cad(song[:titleDispLen])
         title=song
         DisplayPos, MoveTime=0,0
       if (songlen < oldlen):
         songadd="                                  "[songlen-oldlen:]
         write_to_cad(songadd)

  
  #Pause to let the PF Cad catchup - maybe
  #time.sleep(delay)



# Main loop
cad = pifacecad.PiFaceCAD()

#cad.lcd.write("OK")

custom_bitmaps()
init_display()
listener = pifacecad.SwitchEventListener(chip=cad)

#for i in range(8):
#  listener.register(i, pifacecad.IODIR_RISING_EDGE, update_pin_text)
listener.register(0, pifacecad.IODIR_RISING_EDGE, pushed_play)
listener.register(1, pifacecad.IODIR_RISING_EDGE, pushed_back)
listener.register(2, pifacecad.IODIR_RISING_EDGE, pushed_forward)
#listener.register(3, pifacecad.IODIR_RISING_EDGE, reset)
listener.register(3, pifacecad.IODIR_RISING_EDGE, clear)
listener.register(4, pifacecad.IODIR_RISING_EDGE, pushed_blight)
listener.register(5, pifacecad.IODIR_RISING_EDGE, slider_in)
listener.register(6, pifacecad.IODIR_RISING_EDGE, slider_left)
listener.register(7, pifacecad.IODIR_RISING_EDGE, slider_right)
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
list=PlayerID+' title ?'
conn.write(list.encode('ascii')+b"\n")
#list="subscribe prefset,playlist"
#conn.write(list.encode('ascii')+b"\n")
try:
 while (rescnt<2):
  #print ("aaa")
  if (songlen>titleDispLen):
    MoveTime+=1
    if (MoveTime>MoveRate):
        MoveTime=0
        if (DisplayPos+titleDispLen>songlen):
            DisplayPos=0
        else:
            DisplayPos+=2
        cad.lcd.set_cursor(0,0)
        dispEnd=DisplayPos+titleDispLen
        write_to_cad(title[DisplayPos:dispEnd])
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

  else:
      if (slider!=0):
          list=str(mult*slider)
          if (mode == 0):
              if (slider>0):
                list=PlayerID+' mixer volume +'+list
              else:
                list=PlayerID+' mixer volume '+list

          else:
              if (slider>0):
                list=PlayerID+' time +'+list
              else:
                list=PlayerID+' time '+list

          slider=0
          #print (list)
          conn.write(list.encode('ascii')+b"\n")

      if (loop==1):
        list=PlayerID+' status'
        loop=0

      else:
        list=PlayerID+' title ?'
        loop=1

      conn.write(list.encode('ascii')+b"\n")
      time.sleep(1) #4*delay)  

      #if (rescnt>0):
      #  rescnt-=1

except:
  cad.lcd.clear()
  listener.deactivate()
  cad.lcd.backlight_off()
