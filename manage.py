#!/usr/bin/env python3

import os
import sys
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
    self.rename, self.image_loc, self.image_files, self.anno_file = self.set_task_info(t_path)

  def __repr__(self):
    return "name: %s\nrename: %s\npath: %s\n# of images: %d\nimage_location: %s\nanno_file: %s" % (self.name,self.rename,str(self.path),len(self.image_files),str(self.image_loc),str(self.anno_file))
    #return "name: %s\nrename: %s\npath: %s\nimage_location: %s\n# of images: %d\nanno_file: %s" % (self.name,self.rename,str(self.path),str(self.image_loc),len(self.image_files),str(self.anno_file))

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
    return "name: %s\nlen(task_list): %d" % (self.name,len(self.task_list))

class TSR:
  def __init__(self, sdir):
    self.name = "TSR"
    self.date = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    self.plist = self.set_project_list(sdir)
    #db = projects[]
    pass

  def __repr__(self):
    return "name: %s\ndate: %s\nlen(plist): %d" % (self.name,self.date,len(self.plist))

#  def __dict__(self):
#    return { "name" : self.name,
#            "date" : self.date,
#            "plist" : self.plist }

  def set_project_list(self, sdir):
    _plist = []
    _dir_list = [ x for x in list(sdir.glob('*')) if x.is_dir() ]
    for d in _dir_list:
      _plist.append(Project(d))
    #pdb.set_trace()
    return _plist

def load_dataset(db_dir):
  # saved pickle check
  pk = Path(db_dir) / 'db_dir.pkl'
  #p = Path(db_dir) / 'db_dir.json'
  #pdb.set_trace()
  tsr_db = ""
  if Path.exists(pk):
    with open(pk, 'rb') as f:
      #tsr_db = dill.load(f) # load TSR class
      tsr_db = pickle.load(f) # load TSR class
      #tsr_db = json.load(f) # load TSR class
  else:
    tsr_db = TSR(db_dir)
    with open(pk, 'wb') as f:
      #dill.dump(tsr_db, f) # save TSR class
      pickle.dump(tsr_db, f) # save TSR class
      #json.dump(tsr_db, f, indent=4) # save TSR class # TODO - to be serialized
  return tsr_db

def override_dataset(tsr_old, tsr_new):
  # copy tsr_new only if the destination file is not exist in tsr_old
  # TODO
  pass

def migrate_dataset(tsr, tdir):
  # make new dataset at tdir include
  # - copy images with renaming
  # - make a new annotation file
  # return new tsr class for sanity check
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

def filter(self, keyword):
  #TODO
  #우선 label로만 filtering하고 attribute는 좀더 고민해보자
  pass

def exclude(self, keyword):
  pass

if __name__ == "__main__":
  if len(sys.argv) == 3:
    s_dir = Path(sys.argv[1].strip())
    if not s_dir.exists():
      print("** %s is not exist **" % s_dir)
      pdb.set_trace()
      exit(0)
    t_dir = Path(sys.argv[2].strip())
    override = False
    if t_dir.exists():
      print("** %s is already exist **" % t_dir)
      print("** Do you want to override? [y/N]: ", end='')
      ans = input()
      if ans is 'y':
        print("** Continued (do override) **")
        override = True
        pass
      else:
        print("** Aborted **")
        exit(0)
    tsr = load_dataset(s_dir)
    tsr_new = integrate_dataset(tsr,t_dir,override=override)
    pdb.set_trace()
  else:
    print("[Usage] ./manage.py [s_dir] [t_dir]")
    print("\ts_dir = dataset source directory")
    print("\tt_dir = target directory to migrate the data")
  pass
