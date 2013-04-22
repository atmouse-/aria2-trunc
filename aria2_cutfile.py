#!/usr/bin/env python2
# vim:fileencoding=utf-8
"""
description: used by aria2c on download stop
usage: append --on-download-stop=aria2_cutfile.py
       to aria2c command
       or:
       call by [aria2c_cutfile.py $1 $2 $LOCATEFILE]
notify: there seems only python2 could handle file
        with "read/write/append" options in open file
        so, keep useing python2 instead
"""

import struct
import sys
import os
TRUNK_SIZE = 16 # trunck flags represent 16KiB each bit

def ipack(sl_4):
  return int("%d"%struct.unpack('>I',sl_4))

def lpack(sl_8):
  return int("%d"%struct.unpack('>Q',sl_8))

class AriaCtlCfg:
  def __init__(self, filename):
    fp = open(filename, 'rb')
    self.VERSION = fp.read(2)
    self.EXTENSION = fp.read(4)
    self.INFO_HASH_LENGTH = ipack(fp.read(4))
    self.INFO_HASH = fp.read(self.INFO_HASH_LENGTH)
    self.PIECES_LENGTH = ipack(fp.read(4))
    self.TOTAL_LENGTH = lpack(fp.read(8))
    self.UPLOAD_LENGTH = lpack(fp.read(8))
    self.BITFIELD_LENGTH = ipack(fp.read(4))
    self.BITFIELD = fp.read(self.BITFIELD_LENGTH)
    self.NUM_IN_FLIGHT_PIECE = ipack(fp.read(4))

    self.INDEX = ipack(fp.read(4))
    self.LENGTH = ipack(fp.read(4))
    self.BITFIELD_LENGTH = ipack(fp.read(4))

    c_flags = 0
    for i in range(self.BITFIELD_LENGTH):
      flag = ord(fp.read(1))
      x = 0
      for j in range(8):
        if ((flag << x) & 255):
          #print("one bit")
          x += 1
          c_flags += 1
        else:
          break
    print(self.LENGTH)
    self.first_block_length = self.INDEX*self.LENGTH + \
        c_flags * TRUNK_SIZE * 1024
    self.c_flags = c_flags

  def echo_info(self):
    print(self.c_flags)
    print(self.first_block_length)

if __name__ == "__main__":
  """call by aria2c"""
  tmp1_id = sys.argv[1]
  tmp2 = sys.argv[2]
  filename = sys.argv[3]
  print(filename)
  # make sure there is file suffix with ".aria2" exist
  a2 = AriaCtlCfg(filename + ".aria2")
  a2.echo_info()
  fa = open(filename , 'rw+b')
  fa.seek(a2.first_block_length)
  fa.truncate()
  fa.close()
  os.remove(filename + ".aria2")
