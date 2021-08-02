#!/usr/bin/env python3

import os
import sys
import argparse
#import pandas
import pickle # vs json
import json
#import dill
from pathlib import Path
import datetime
import re
import pdb

class Task:
  def __init__(self, t_path):
    self.path = t_path
    self.name = t_path.name
    self.shortname, self.image_loc, self.image_files, self.anno_file = self.set_task_info(t_path)

  def __repr__(self):
    return "{name: %s, shortname: %s, path: %s, # of images: %d, image_location: %s, anno_file: %s}" % (self.name,self.shortname,str(self.path),len(self.image_files),str(self.image_loc),str(self.anno_file))
    #return "name: %s\nshortname: %s\npath: %s\nimage_location: %s\n# of images: %d\nanno_file: %s" % (self.name,self.shortname,str(self.path),str(self.image_loc),len(self.image_files),str(self.anno_file))

  def set_task_info(self, path):
    # read coco format
    # task_dir
    #  ├── anoatation
    #  │   └── instances_default.json
    #  └── images
    #      └── [folders]
    #          └── ...
    #              └── *.jpg, jpeg, png, bmp
    _anno_files = list(path.rglob('instances_default.json'))
    _anno_file = _anno_files[0]
    if len(_anno_files) > 1:
      print("** There are serveral annotation files more than 1 in a single Task **")
      pdb.set_trace()

    _image_files_all = []
    _image_loc = []
    image_format_support = ['jpg', 'jpeg', 'png', 'bmp']
    for img_fmt in image_format_support:
      _image_files = list(path.rglob('*.'+img_fmt))
      for i in _image_files:
        if i.parent in _image_loc:
          pass
        else:
          _image_loc.append(i.parent)
      _image_files_all += _image_files
    if len(_image_loc) > 1:
      print("** There are serveral separated image folders in a single Task **")
      print("** Image files' name will be changed as follow the first folder name **")
      pdb.set_trace()
    else:
      _image_loc = _image_loc[0]

    _name = str(_image_loc)
    if '/images/' in _name:
      _name = _name.split('/images/')[1]
    else:
      _name = ""
    # if no subdir in /images, the split()[1] might be empty or invalid
    # in order to integrate between old(/images/*.jpg) and new dataset, to do this
    _name = re.sub('[^a-zA-Z0-9_/\-]', '', _name)
    _name = _name.replace('-','_').replace('/', '-')
    #pdb.set_trace()
    return _name, _image_loc, _image_files_all, _anno_file

class Project:
  def __init__(self, p_path):
    self.name = p_path.name
    self.task_list = [ Task(x) for x in list(p_path.iterdir()) if x.is_dir() ]

  def __repr__(self):
    return "{name: %s, len(task_list): %d}" % (self.name,len(self.task_list))

class TSR:
  def __init__(self, sdir):
    self.name = "TSR"
    self.path = str(sdir)
    self.date_created = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    self.plist = self.set_project_list(sdir)

  def __repr__(self):
    return "name: %s\ndate_created: %s\nlen(plist): %d" % (self.name,self.date_created,len(self.plist))

  def set_project_list(self, sdir):
    _plist = []
    _dir_list = [ x for x in list(sdir.glob('*')) if x.is_dir() ]
    for d in _dir_list:
      _plist.append(Project(d))
    #pdb.set_trace()
    return _plist

def override_dataset(tsr_old, tsr_new):
  # copy tsr_new only if the destination file is not exist in tsr_old
  # TODO
  pass


def integrate_dataset(tsr, tdir, override=False):
  if override:
    tsr_new = tsr
    tsr_old = TSR(tdir)
    override_dataset(tsr_old, tsr_new)
  else:
    tsr_new = migrate_dataset(tsr, tdir)
  return tsr_new

#TODO list
def save_coco(self):
  #TODO
  pass

def save_yolo(self):
  #TODO
  pass


def exclude(self, keyword):
  pass

def make_db_table(_dir):
  _tsr = TSR(_dir)
  return _tsr

def migrate(s_dir, t_dir):
  '''
  migrate(s_dir, t_dir):
    :return: new_tsr
    migrate dataset from source dir to target dir
    this include
    - make a table file of s_dir in not exist
    - copy images with renaming from s_dir to t_dir
    - make a new annotation file for t_dir
    - gen a new table file for t_dir
    - return new tsr class for sanity check
  '''
  print("do migrate")

  #t_dir empty check
  tp = Path(t_dir)
  if not tp.exists():
    print("* the t_dir %s is not exist -> make a new dir *" % t_dir)
    tp.mkdir()
  elif not tp.is_dir():
    print("* the t_dir %s exist but not a dir -> abort *" % t_dir)
    return None
  elif len(list(tp.iterdir())) > 0:
    #tdir is alread exist and not empty
    print("* the t_dir %s exist but not emtpy -> please use \"update\" *" % t_dir)
    return None

  #s_dir exist check
  sp = Path(s_dir)
  if not sp.exists():
    print("* the s_dir %s is not exist -> abort *" % s_dir)
    return None

  #s_dir table file check
  st_pkl = Path(s_dir) / "db_table.pkl"
  if st_pkl.exists():
    #s_dir table load
    print("* s_dir db_table.pkl file already exist -> load db_table.pkl *")
    with open(st_pkl, 'rb') as f:
      tsr_table = pickle.load(f) # load TSR class
      #tsr_table = json.load(f) # load TSR class
      #tsr_table = dill.load(f) # load TSR class
  else:
    #s_dir table create
    print("* s_dir db_table.pkl file is not exist -> make new TSR & save pkl")
    tsr_table = TSR(Path(s_dir))
    #s_dir table save
    with open(st_pkl, 'wb') as f:
      pickle.dump(tsr_table, f) # save TSR class
      #json.dump(tsr_table, f, indent=4) # save TSR class # TODO - to be serialized
      #dill.dump(tsr_table, f) # save TSR class

  # copy and generate t_dir dataset #
  print("do copy and gen tdir")
  pdb.set_trace()
  #tp = Path(t_dir) #done above
  tp_task = tp / "project_0" / "task_0"
  tp_anno = tp_task / "annotations"
  tp_image = tp_task / "images"
  common_cat = {}
  for p in tsr_table.plist:
    for t in p.task_list:
      task_mapping_info = {}
      task_mapping_info['org_task_name'] = t.name
      rname= t.shortname
      img_loc = Path(t.image_location)
      with open(t.anno_file, 'r') as f:
        anno = json.load(f)
        # dummy info -> do nothing, later
        # category check
        if bool(common_cat):
          common_cat = anno['categories']
        catmap = # TODO
        # licneses stacking
        # image mapping
        for img in anno['images']:
          img['id']
        # annotations remapping

  #make new tsr
  print("make new tsr")
    #? dir read만 하면 되는거 아닌가?
    #save table in t_dir
  #return new tsr
  return tsr_table

def update():
  '''
  update(s_dir, t_dir):
    :return: ?
    Almost same to migrate but here open the t_dir TSR table and update new data with checking file exist
    (if exist -> pass, if not -> add)
    !Warning! This can make duplicate case
  '''
  pass

def extract():
  '''
  filter_(condition, s_dir, t_dir):
    :return: TSR?
    condition = include [] or exclude []
    read s_dir's TSR table file and
    choose some data which fit the condition
  '''
  pass

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="TSR db manager")
  parser.add_argument('command', choices=['migrate', 'update', 'extract'],metavar='command', type=str, help="Among \"migrate, update, extract\", choose command what you want to do")
  parser.add_argument('-s','--sdir', metavar='PATH', type=str, help="source directory")
  parser.add_argument('-t','--tdir', metavar='PATH', type=str, help="target directory")
  parser.add_argument('-i','--include', metavar='LABEL', type=str, nargs='+', help="including conditions for filtering")
  parser.add_argument('-x','--exclude', metavar='LABEL', type=str, nargs='+', help="excluding conditions for filtering")

  args = parser.parse_args()
#  print(args.accumulate(args.integers))

  pdb.set_trace()
  if args.command == "migrate":
    # option --sdir, tdir check
    if args.sdir == None:
      ans = input("command \"migrate\" require --sdir. continue as default? [default=./results] [Y/n]: ")
      if (ans == 'y') or (ans == 'Y') or (ans == ''):
        args.sdir = "./results"
        print("* sdir = %s *" % args.sdir)
      else:
        print("* sdir is not decided -> abort *")
        exit(0)
    if args.tdir == None:
      ans = input("command \"migrate\" require --tdir. continue as default? [default=./tsr] [Y/n]: ")

      if (ans == 'y') or (ans == 'Y') or (ans == ''):
        args.tdir = "./tsr"
        print("* tdir = %s *" % args.tdir)
      else:
        print("* sdir is not decided -> abort *")
        exit(0)
    ntsr = migrate(args.sdir, args.tdir)
    if ntsr == None:
      print("* the migration ended abnormally, please refer the error code *")
      exit(0)
  elif args.command == "update":
    # option --tdir check
    update() # do sth
  elif args.command == "extract":
    # option -i, -x check
    extract() # do sth
  else:
    args.__repr__()
