PifaceCad_Squeeze
=================

Use a Raspberry Pi with PiFace Control and Display as a display for a SqueezeBox player

This initial version assumes a squeezelite player on the same machine in order to get the MAC address used. In the long run, this will work with any player, and it does not even need to be on the local machine as it communicates with the Squeeze Server.

 Button usage:
 0: Play/Pause
 1: Previous track
 2: Next track
 3: Not used.
 4: Backlight On/Off
 5: Switch mode (volume/Seek)
 6: Volume Down/ Seek back (-30 seconds)
 7: Volume Up/ Seek forward (+30 seconds)

 Requires: The default Python3 pifacecad libraries

 apt-get install python3-pifacecad

Version 0.1
===========

 Initial version: Manages to display volume, play/pause, and the current song title.

 Falls foul of the CaD race issue, and garbles the display if things happen too quickly, mostly if you change volume too quick.
