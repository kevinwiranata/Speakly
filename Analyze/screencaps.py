import sys
import argparse
import cv2
import os
from pydub import AudioSegment

filename = sys.argv[1]
#filename = "test4.mp4"
name = filename[:-4]

if not os.path.exists("images/" + name):
  os.makedirs("images/" + name)

count = 0
vidcap = cv2.VideoCapture("uploads/" + filename)
success,image = vidcap.read()
while success:
  #print ('Read a new frame: ', success)
  cv2.imwrite("images/" + name + "/frame{}.jpg".format(count), image)     # save frame as JPEG file
  count = count + 1

  #print(count * 1000)
  vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))    # added this line 
  success,image = vidcap.read()
  #print(count)
  #print(success)
  if count > vidcap.get(cv2.CAP_PROP_FRAME_COUNT)/vidcap.get(cv2.CAP_PROP_FPS): # length of video
    break


audio = AudioSegment.from_file("uploads/" + filename, "mp4")
audio.export("audio/stereo/{}.flac".format(name), format = "flac")