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


  if args.command == "migrate":
    # option --sdir, tdir check
    if args.sdir == None:
      try:
        args.sdir = Input('tx',"* command \"migrate\" require --sdir *", "[default=./results]")
        print("-> sdir = %s" % args.sdir)
      except:
        print("** sdir is not decided -> abort **")
        exit(0)
    if args.tdir == None:
      try:
        args.tdir = Input('tx',"* command \"migrate\" require --tdir? *", "[default=./tsr]")
        print("-> tdir = %s" % args.tdir)
      except:
        print("** tdir is not decided -> abort **")
        exit(0)

    s_db = db.DB(args.sdir)
    t_db = cmds.migrate(s_db, args.tdir, renameTF=not args.no_rename)
    #t_db = cmds.migrate(s_db, args.tdir, extractors=ext, tv_ratio=args.ratio, renameTF=not args.no_rename)
    if t_db == None:
      print("** the migration ended abnormally please refer the error code **")
      exit(0)
  ###############################################
  elif args.command == "extract":
    # option --sdir, tdir check
    if args.sdir == None:
      try:
        args.sdir = Input('tx',"* command \"extract\" require --sdir *", "[default=./results]")
        print("-> sdir = %s" % args.sdir)
      except:
        print("** sdir is not decided -> abort **")
        exit(0)
    if args.tdir == None:
      try:
        args.tdir = Input('tx',"* command \"extract\" require --tdir? *", "[default=./tsr]")
        print("-> tdir = %s" % args.tdir)
      except:
        print("** tdir is not decided -> abort **")
        exit(0)

    ext = []
    if args.label_include == None and args.label_exclude == None:
      print("** There is no extractor -> abort **")
      exit(0)
    if args.label_include != None:
      ext.append(['label', 'in'] + list(args.label_include))
    if args.label_exclude != None:
      ext.append(['label', 'ex'] + list(args.label_exclude))

    s_db = db.DB(args.sdir)
    t_db = cmds.migrate(s_db, args.tdir, extractors=ext, renameTF=not args.no_rename)
    #t_db = cmds.migrate(s_db, args.tdir, extractors=ext, tv_ratio=args.ratio, renameTF=not args.no_rename)
    if t_db == None:
      print("** the migration ended abnormally please refer the error code **")
      exit(0)
  ###############################################
  elif args.command == "divide":
    # option --sdir, tdir check
    if args.sdir == None:
      try:
        args.sdir = Input('tx',"* command \"extract\" require --sdir *", "[default=./results]")
        print("-> sdir = %s" % args.sdir)
      except:
        print("** sdir is not decided -> abort **")
        exit(0)
    if args.tdir == None:
      try:
        args.tdir = Input('tx',"* command \"extract\" require --tdir? *", "[default=./tsr]")
        print("-> tdir = %s" % args.tdir)
      except:
        print("** tdir is not decided -> abort **")
        exit(0)

    s_db = db.DB(args.sdir)
    t_db = None
    if args.tv_file == None and args.tv_ratio==1.0:
      print("** no train/valid divide policy (tv_file or tv_ratio) -> abort **")
      exit(0)
    elif args.tv_file != None:
      t_db = cmds.migrate(s_db, args.tdir, tv_file=args.tv_file, renameTF=not args.no_rename)
    else:
      t_db = cmds.migrate(s_db, args.tdir, tv_ratio=args.tv_ratio, renameTF=not args.no_rename)

    if t_db == None:
      print("** the migration ended abnormally please refer the error code **")
      exit(0)
  ###############################################
  elif args.command == "stat_only":
    # option --sdir only
    if args.sdir == None:
      try:
        args.sdir = Input('tx',"* command \"migrate\" require --sdir *", "[default=./tsr]")
        print("-> sdir = %s" % args.sdir)
      except:
        print("** sdir is not decided -> abort **")
        exit(0)

    #################################################
    ## TODO - HERE 2021.09.09
    ## check db status about labels and attributes
    #################################################

    s_db = db.DB(args.sdir)
    s_db.pdb_display()
  else:
    print("** commnads is not decided **")
    args.__repr__()
