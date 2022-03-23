#!/usr/bin/env python3

#############
# manage.py 
# check arguments and run the commands #
#
# How to use
# python manage.py ../smokingVSnotsmoking merge ../smokingVSnotsmoking/smo_all.json
# python manage.py ../COCO2017/annotations/instances_val2017.json filter ../COCO2017/pho_val.json 77
# python manage.py ../COCO2017 filter _cup 47
#
# let you know
# filter multiple class regards as "and" not "or"
#############

import os
import sys
import argparse
#import pandas
import json
from pathlib import Path
import datetime
import re
import shutil
import pdb

#from pytools.uinputs import Input
#from pytools import tsr
#from pytools import db
import commands as cmds

if __name__ == "__main__":

  ####################
  #### path check ####
  if len(sys.argv) <= 2:
    print("** target path is empty **")
    t_path = input("path:")
  else:
    t_path = sys.argv[1]
  p = Path(t_path)
  print("working dir:", p.resolve())
  if not p.is_dir():
    print("** there is no directory %s **" % p.resolve())
    exit(0)

  ###############################
  #### anno file list choose ####
  annos = list(map(str,list(p.rglob('*.json'))))
  print("## found annoataion files ##")
  print("# please edit the list in order to include meaningful flie only #")
  print("# ex) annos = [ x for x in annos if 'phone' in x ] #")
  print(annos)
  pdb.set_trace()

  ###############################
  #### commands              ####
  cmd = ''
  if len(sys.argv) >= 3:
    cmd = sys.argv[2]
  elif len(sys.argv) < 3 or cmd == '':
    print("** commands is not decided **")
    cmd = input("cmd:")

  if cmd == "filter":
    cmds.filter(p, annos, sys.argv[3:])
  elif cmd == "merge":
    cmds.merge(p, annos, sys.argv[3:])
  else:
    print("** there is no commands %s **" % cmd)
    pass

  print("commands done.")
  pdb.set_trace()
  exit(1)
