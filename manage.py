#!/usr/bin/env python3

#############
# manage.py 
# check arguments and run the commands #
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

from pytools.uinputs import Input
from pytools import tsr
from pytools import db
from pytools import commands as cmds

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="TSR db manager")
  parser.add_argument('command', choices=['migrate', 'update', 'extract', 'stat_only'],metavar='command', type=str, help="Among \"migrate, update, extract, stat_only\", choose command what you want to do")
  parser.add_argument('-s','--sdir', metavar='PATH', type=str, help="source directory")
  parser.add_argument('-t','--tdir', metavar='PATH', type=str, help="target directory")
  parser.add_argument('-i','--include', metavar='LABEL', type=str, nargs='+', help="including conditions for filtering. divide as space")
  parser.add_argument('-x','--exclude', metavar='LABEL', type=str, nargs='+', help="excluding conditions for filtering. divide as space")
  parser.add_argument('-r','--ratio', metavar='FLOAT', type=float, default=1.0, help="train/validation ratio [0,1]; 1 = all training, 0 = all validation")
  parser.add_argument('-n','--no_rename', action='store_true', help="do not rename image files when migration, default: False")

  args = parser.parse_args()
#  print(args.accumulate(args.integers))

  ###############################################
  #### commands                              ####
  ###############################################
  if args.command == "migrate":
    # option --sdir, tdir check
    if args.sdir == None:
      if Input('yn',"* command \"migrate\" require --sdir. continue as default? [default=./results] *", "[Y/n]"):
        args.sdir = "./results"
        print("-> sdir = %s" % args.sdir)
      else:
        print("** sdir is not decided -> abort **")
        exit(0)
    if args.tdir == None:
      if Input('yn',"* command \"migrate\" require --tdir. continue as default? [default=./tsr] *", "[Y/n]"):
        args.tdir = "./tsr"
        print("-> tdir = %s" % args.tdir)
      else:
        print("** tdir is not decided -> abort **")
        exit(0)
    s_db = db.DB(args.sdir)
    pdb.set_trace()
    t_db = cmds.migrate(s_db, args.tdir, tv_ratio=args.ratio, renameTF= (not args.no_rename) )
    if t_db == None:
      print("** the migration ended abnormally, please refer the error code **")
      exit(0)
  ###############################################
  elif args.command == "update":
    # option --tdir check
    update() # do sth
  ###############################################
  elif args.command == "extract":
    # option --sdir, tdir check
    if args.sdir == None:
      if Input('yn',"* command \"extract\" require --sdir. continue as default? [default=./tsr] *", "[Y/n]"):
        args.sdir = "./tsr"
        print("-> sdir = %s" % args.sdir)
      else:
        print("** sdir is not decided -> abort **")
        exit(0)
    if args.tdir == None:
      if Input('yn',"* command \"extract\" require --tdir. continue as default? [default=./tsr_ex] *", "[Y/n]"):
        args.tdir = "./tsr_ex"
        print("-> tdir = %s" % args.tdir)
      else:
        print("** tdir is not decided -> abort **")
        exit(0)
    # option -i, -x check
    if (args.include == None) and (args.exclude == None):
      print("** command \"extract\" require --include or --exclude at least one. **")
      exit(0)
    if (args.include != None) and (args.exclude != None):
      print("** command \"extract\" require --include or --exclude at most one. **")
      exit(0)
    # TODO 1 - make ,(comma) separation with args parse
    # TODO 2 - getting input when it is empty
    if args.include != None:
      ext = cmds.includer(args.include)
    elif args.exclude != None:
      ext = cmds.excluder(args.exclude)
    ntsr = migrate(args.sdir, args.tdir, extractor = ext)
    if ntsr == None:
      print("** the migration ended abnormally, please refer the error code **")
      exit(0)
    # TODO adv extractor - handle label and attribute too
    #                      suggest) read selection file (ex. --extract-file stop_sign.config) composed to some formatted context
  ###############################################
  elif args.command == "stat_only":
    # option --sdir only
    if args.sdir == None:
      if Input('yn',"* command \"stat_only\" require --sdir. continue as default? [default=./tsr] *", "[Y/n]"):
        args.sdir = "./tsr"
        print("-> sdir = %s" % args.sdir)
      else:
        print("** sdir is not decided -> abort **")
        exit(0)
    # json exist test
    st_json = Path(args.sdir) / "db_table.json"
    if st_json.exists():
      # ask whether renew the table json
      if Input('yn',"* s_dir db_table.json file already exist. Do you want to renew the db_table.json? *", "[y/N]"):
        #s_dir table create & save
        tsr_table_new = tsr.TSR(Path(args.sdir))
        with open(st_json, 'w') as f:
          pdb.set_trace()
          json.dump(tsr_table_new, f, indent=4, default=tsr.json_encoder, ensure_ascii=False, sort_keys=True)
          print("* s_dir db_table.json is renewed *")
      else:
        print("* s_dir db_table.json already exist -> read & continue *")

    # s_dir table load
    with open(st_json, 'r') as f:
      tsr_table_json = json.load(f)
    tsr_table = tsr.TSR(tsr_table_json)
    # print tsr_table
    print(tsr_table)
    for p in tsr_table.plist:
      print('\t',p)
      for t in p.task_list:
        print('\t\t',t)

    db_viewer = db.DB_viewer(tsr_table)
    db_viewer.interactive()

  else:
    args.__repr__()
