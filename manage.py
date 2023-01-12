#!/usr/bin/env python3

#############
# manage.py 
# check arguments and run the commands #
#
# Usual process 
# 0. help
# 1. manifest <-> convert
# 2. fitler
# 3. merge (img copy)
# 4. divide (img copy)
# or 3+4. merge & divide (img copy)
#
# How to use
# python manage.py [command] [--source]
#
#
# python manage.py ../smokingVSnotsmoking merge ../smokingVSnotsmoking/smo_all.json
#                  [ dataset dir        ] merge [ output annotation file          ]
# python manage.py ../COCO2017/annotations/instances_val2017.json filter ../COCO2017/pho_val.json 77
#                  [ a single annotation file input             ] filter [ single output file   ] [category id]
# python manage.py ../COCO2017 filter _cup 47
#                  [ db dir  ] filter [tag] [cat id] <- use for multiple annotaiton file
# python manage.py ../COCO2017/coco_pho_cup_bottle.json copy ~/datasets/coco_pcb train=1 val=0
#                  [ a single anno file input         ] copy [ target dir      ] train=[train ratio] val=[valid ratio]
#
# let you know
# filter multiple class regards as "and" not "or"
#############

import os
import sys
import argparse

#import pandas
#import json
#from pathlib import Path
#import datetime
#import re
#import shutil
import pdb
#import commands as cmds

def parse_opt(known=False):
  parser = argparse.ArgumentParser()
  parser.add_argument('command', type=str, default='', help='support singular command. [manifest, filter, merge, divide, md (merge & divide)]')
  parser.add_argument('--cfg', type=str, default='', help='model.yaml path')

  pdb.set_trace()
  opt = parser.parse_known_args()[0] if known else parser.parse_args()
  return opt

if __name__ == "__main__":
  if len(sys.argv) <= 2:
    print("** manage.py require commands **")
    exit(0)
  #else
  #cmd = sys.argv[1]
  opt = parse_opt()

  if opt.command == "manifest":
    import utils.manifest as cmd
    cmd.run()

  # 2023.01.05 idea
  #   make a recipe file (ex, testv1.recipe) to read and execute

  pdb.set_trace()
#  ####################
#  #### path check ####
#  if len(sys.argv) <= 2:
#    print("** source path/file is empty **")
#    t_path = input("path:")
#  else:
#    t_path = sys.argv[1]
#  ps = Path(t_path)
#  print("working dir/file:", ps.resolve())
#  if not ps.exists():
#    print("** there is no dir/file %s **" % ps.resolve())
#    exit(0)
#
#  ###############################
#  #### commands              ####
#  cmd = ''
#  if len(sys.argv) >= 3:
#    cmd = sys.argv[2]
#  elif len(sys.argv) < 3 or cmd == '':
#    print("** commands is not decided **")
#    cmd = input("cmd:")
#
#  ###############################
#  #### anno file list choose ####
#  if ps.is_dir():
#    annos = list(map(str,list(ps.rglob('*.json'))))
#    print("## found annoataion files ##")
#    print("# please edit the list in order to include meaningful flie only #")
#    print("# ex) annos = [ x for x in annos if 'phone' in x ] #")
#    print("annos=", annos)
#    pdb.set_trace()
#  elif ps.is_file():
#    annos = [str(ps.name)]
#    ps = ps.resolve().parent
#  else:
#    print("## there is no support file format")
#    exit(0)
#
#  ###############################
#  #### execution             ####
#  if cmd == "filter":
#    cmds.filter(ps, annos, sys.argv[3:])
#  elif cmd == "merge":
#    cmds.merge(ps, annos, sys.argv[3:])
#  elif cmd == "copy":
#    cmds.copy(ps, annos[0], sys.argv[3:])
#  else:
#    print("** there is no commands %s **" % cmd)
#    pass
#
#  print("commands done.")
#  pdb.set_trace()
#  exit(1)
