import serial
import time
import sys
import struct
import ConfigParser
import sqlite3

import os, subprocess

files = os.listdir('./')

overwrite = False

for sourceVideo in files:
    if sourceVideo[-4:] != ".mp3" and sourceVideo[-4:] != ".wav":
        continue
    infile = sourceVideo
    destinationVideo = "../" + sourceVideo[:-4] + ".raw"
    if ( os.path.isfile(destinationVideo)  and not overwrite):
           print destinationVideo
    else:
        cmdLine = ['ffmpeg', '-i', infile, '-f', 's16le', '-acodec', 'pcm_s16le','-ar','8000',"-y",destinationVideo]
        subprocess.call(cmdLine)


#"-vol","100",