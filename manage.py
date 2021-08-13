#!/usr/bin/env python3

import os
import sys
import argparse
#import pandas
import pickle # vs json
import json
from pathlib import Path
import datetime
import re
import shutil
import pdb

def yntest(message, default):
  '''
    message : display text
    default : string with [y/n] choices
    return : y -> T, n -> F
  '''
  redo_msg = ''
  while True:
    ans = input(redo_msg + message + ' ' + default + ': ')
    if ('y' in ans) or ('Y' in ans):
      return True
    elif ('n' in ans) or ('N' in ans):
      return False
    elif ans == '':
      if 'Y' in default:
        return True
      elif 'N' in default:
        return False
      else:
        print("** There is no default option. Please retry **")
    else:
      print("** There is wrong input. Please retry **")
    redo_msg = 're: '

def txtest(message, default):
  '''
    message : display text
    default : return when in '' (empty string)
    return : input text list
  '''
  redo_msg = ''
  while True:
    ans = input(redo_msg + message + ': ')
    if ans == '':
      return default
    else:
      return ans.split(' ')
    redo_msg = 're: '

class Task():
  def __init__(self, t_path):
    self.path = t_path
    self.name = t_path.name
    self.shortname, self.image_loc, self.image_files, self.anno_file = self.set_task_info(t_path)
    self.num_image = len(self.image_files)

  def __repr__(self):
    return "{name: %s, shortname: %s, path: %s, # of images: %d, image_location: %s, anno_file: %s}" % (self.name,self.shortname,str(self.path),len(self.image_files),str(self.image_loc),str(self.anno_file))
    #return "name: %s\nshortname: %s\npath: %s\nimage_location: %s\n# of images: %d\nanno_file: %s" % (self.name,self.shortname,str(self.path),str(self.image_loc),len(self.image_files),str(self.anno_file))

#  def __iter__(self):
#    for key in self.__dict__:
#      yield key, getattr(self, key)

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
      _image_files.sort()
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
    return _name, _image_loc, _image_files_all, _anno_file

class Project():
  def __init__(self, p_path):
    self.name = p_path.name
    self.task_list = [ Task(x) for x in list(p_path.iterdir()) if x.is_dir() ]
    self.num_task = len(self.task_list)

  def __repr__(self):
    return "{name: %s, num_task: %d}" % (self.name,self.num_task)

#  def __iter__(self):
#    for key in self.__dict__:
#      yield key, getattr(self, key)

class TSR:
  def __init__(self, sdir):
    self.name = "TSR"
    self.path = str(sdir)
    self.date_created = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    self.plist = self.set_project_list(sdir)

  def read_dict(self, r_dic):
    for key in r_dic:
      if 'name' == key:
        self.name = r_dic[key]
        # TODO
        # the function is a kind of copy constructor for json loading
        # please refer the other comments by searching "json_decoder"
      pass

  def __repr__(self):
    return "name: %s\ndate_created: %s\nlen(plist): %d" % (self.name,self.date_created,len(self.plist))

  #def __dict__(self):
  #  return {'name': self.name, 'path': self.path, 'date_created': self.date_created, 'plist': [ p.__dict__ for p in self.plist]}

#  def __iter__(self):
#    for key in self.__dict__:
#      yield key, getattr(self, key)
    #return {'name': self.name, 'path': self.path, 'date_created': self.date_created, 'plist': [ p.__dict__ for p in self.plist]}

  def set_project_list(self, sdir):
    _plist = []
    _dir_list = [ x for x in list(sdir.glob('*')) if x.is_dir() ]
    for d in _dir_list:
      _plist.append(Project(d))
    #pdb.set_trace()
    return _plist

def json_encoder(o):
  if isinstance(o, TSR):
    return o.__dict__
  elif isinstance(o, Project):
    return o.__dict__
    #return {'__Project__': o.__dict__}
  elif isinstance(o, Task):
    return o.__dict__
  elif isinstance(o, Path):
    return str(o)
  raise TypeError('not JSON serializable')

#def json_decoder(o):
#  if 'TSR' == o: ... TODO
# to be set a proper constructors for each classes
# refer the other comments which searched by "json_decoder"

def migrate(s_dir, t_dir, extractor=None):
  #TODO extractor add
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
  if extractor == None:
    extractor = lambda x : True

  #t_dir empty check
  tp = Path(t_dir)
  if not tp.exists():
    print("* t_dir %s is not exist -> make a new dir *" % t_dir)
    tp.mkdir()
    pass
  elif not tp.is_dir():
    print("** t_dir %s exist but not a dir -> abort **" % t_dir)
    return None
  elif len(list(tp.iterdir())) > 0:
    #tdir is alread exist and not empty
    if not yntest("* t_dir %s exist but not emtpy -> please use \"update\" *\n* do you want to *DELETE* all and make a new ? *" % t_dir, "[y/N]"):
      return None
    else: # continue
      shutil.rmtree(tp)
      tp.mkdir()
      pass

  #s_dir exist check
  sp = Path(s_dir)
  if not sp.exists():
    print("** the s_dir %s is not exist -> abort **" % s_dir)
    return None

  #s_dir table file check
  print("[%s] s_dir table file check" % datetime.datetime.now().strftime('%H:%M:%S'))
  #st_pkl = Path(s_dir) / "db_table.pkl"
  st_json = Path(s_dir) / "db_table.json"
  #if st_pkl.exists():
  if st_json.exists():
    #s_dir table load
    print("* s_dir db_table.pkl file already exist -> load db_table.pkl *")
    #with open(st_pkl, 'rb') as f:
    with open(st_json, 'r') as f:
      #tsr_table = pickle.load(f) # load TSR class
      tsr_table = json.load(f) # load TSR class
  else:
    #s_dir table create
    #print("* s_dir db_table.pkl file is not exist -> make new TSR & save pkl")
    print("* s_dir db_table.json file is not exist -> make new TSR & save json")
    tsr_table = TSR(Path(s_dir))
    #s_dir table save
    #with open(st_pkl, 'wb') as f:
    with open(st_json, 'w') as f:
      #pickle.dump(tsr_table, f) # save TSR class
      json.dump(tsr_table, f, indent=4) # save TSR class # TODO - to be serialized

  # copy and generate t_dir dataset #
  # TODO(changmin) : making as a function of some class object would be botter...
  #                  candidate = TSR? or else?
  print("[%s] do copy and gen tdir" % datetime.datetime.now().strftime('%H:%M:%S'))
  print("[%s] %d Project / %d tasks in sdir" % (datetime.datetime.now().strftime('%H:%M:%S'),len(tsr_table.plist), sum(list(len(p.task_list) for p in tsr_table.plist))))
  def categories_cmp(cm, an):
    '''
    return dictionary which id(int) to id(int)
    '''
    res_dict = {}
    info_dict = []
    for cat_an in an:
      _name = cat_an['name']
      s_id = cat_an['id']
      t_id = 0
      if extractor(_name): # T: to be include
        for cat_cm in cm:
          if _name == cat_cm['name']:
            t_id = cat_cm['id']
            break
        if t_id == 0:
          #if yntest("* the task has more categories than original one *\n* do you want to expand categories set and continue the migration? *", "[y/N]"):
          max_t_id = max([ x['id'] for x in cm]) if cm else 0 #if not empty -> max
          t_id = max_t_id + 1
          cm.append({"id": t_id,
                     "name": _name,
                     "supercategory":""
                     })
          # extend always
          #pass
          #else:
          #  return None, None
      else: # excluded label -> skipping
        pass # keep t_id = 0
      res_dict[s_id] = t_id
      info_dict.append({"name":_name, "id_change":"%d->%d"%(s_id, t_id)})
    return res_dict, info_dict

  #tp = Path(t_dir) #done above
  tp_pj_task_name = "project_0/task_0"
  tp_pj = tp / "project_0"
  tp_task = tp_pj / "task_0"
  tp_anno = tp_task / "annotations"
  tp_image = tp_task / "images"
  tp_anno.mkdir(parents=True)
  tp_image.mkdir(parents=True, exist_ok=True)
  #common_cat = {}
  common_cat = []
  new_anno_json = {}
  new_anno_json['images'] = []
  new_anno_json['annotations'] = []

  g_img_id = 0
  g_anno_id = 0
  # for project
  #   for task
  #     0) categories check
  #     1) copy images
  #     2) make annotation detail
  all_migration_info = {} # {project{task[cat_id_map, img_id_map]}}
  all_migration_info['project_info'] = []
  #print("[%s] do copy and gen tdir" % datetime.datetime.now().strftime('%H:%M:%S'))
  #####################################################################
  ## project loop ##
  ##################
  for p in tsr_table.plist:
    project_mapping_info = {}
    project_mapping_info['name'] = p.name
    project_mapping_info['task_info'] = []
    print(" project %s start" % p.name)
    ###################################################################
    ## task loop ##
    ###############
    for t in p.task_list:
      print("  task %s start" % t.name)
      task_mapping_info = {}
      task_mapping_info['org_task_name'] = t.name
      task_mapping_info['cat_id_map'] = []
      task_mapping_info['img_id_map'] = []
      # anno_file(instances_default.json) read
      with open(t.anno_file, 'r') as f:
        anno = json.load(f)

        # 0) category check
        #if not bool(common_cat):
        #  common_cat = anno['categories']
        # do comparision, return anno's cat's id -> common cat's id dict
        cat_id_map, task_mapping_info['cat_id_map'] = categories_cmp(common_cat, anno['categories'])
        if cat_id_map == None:
          print("* categories_cmp ends with error *")
          print("** aborted **")
          exit(0)
        print("  cat_id_map:", cat_id_map)
        # make categories # do later at end of project loop

        # 0-1) extractor remove no labeling image
        img_copy_list_id = set()
        for an in anno['annotations']:
          if cat_id_map[an['category_id']] != 0:
            img_copy_list_id.add(an['image_id'])

        # 1) image copy
        #    include copy & rename
        l_img_id = 0
        img_id_map = {}
        ###############################################################
        ## image loop ##
        ################
        for img in anno['images']:
          if img['id'] not in img_copy_list_id:
            continue
          # img file copy
          org_name = img['file_name'].split('/')[-1]
          file_format = img['file_name'].split('.')[-1]
          #org_name = Path(img['file_name']).name
          org_file = t.image_loc / org_name
          new_name = org_name if t.shortname == '' else t.shortname + '_' + str(l_img_id) + '.' + file_format
          new_file = tp_image / new_name
          try:
            shutil.copyfile(org_file, new_file)
          except:
            print("** shutil.copy sth wrong **")
            pdb.set_trace()
          _info_str = str(org_file) + ' -> ' + str(new_file)
          task_mapping_info['img_id_map'].append(_info_str)
          print("  cp", _info_str)

          # id matching # will be used for annotations['image_id']
          org_id = img['id']
          new_id = g_img_id
          img_id_map[org_id] = new_id
          new_anno_json['images'].append({ "id": g_img_id,
                                          "width": img["width"],
                                          "height": img["height"],
                                          "license": img["license"],
                                          "file_name": tp_pj_task_name+'/images/'+new_name,
                                          "flickr_url": img["flickr_url"],
                                          "coco_url": img["coco_url"],
                                          "date_captured": img["date_captured"]
                                          })
          g_img_id += 1
          l_img_id += 1

        print("  anno[\'annoatation\'] start")
        # 2) make annotations detail
        for an in anno['annotations']:
          if cat_id_map[an['category_id']] != 0:
            new_anno_json['annotations'].append({"id": g_anno_id,
                                                 "image_id": img_id_map[an['image_id']],
                                                 "category_id": cat_id_map[an['category_id']],
                                                 "segmentation": an['segmentation'],
                                                 "area": an['area'],
                                                 "bbox": an['bbox'],
                                                 "iscrowd": an['iscrowd'],
                                                 "attributes": an['attributes']
                                                 })
            g_anno_id += 1
        print("  anno[\'annoatation\'] done")
        #pdb.set_trace()
        # TODO(changmin): supercategory = ''
      project_mapping_info['task_info'].append(task_mapping_info)
    # end for task_list:
    all_migration_info['project_info'].append(project_mapping_info)
  # end for tsr_table.plist:
  tp_info = tp / "migration_info.json"
  with open(tp_info, 'w') as f:
    json.dump(all_migration_info, f, indent=4)

  # 4) make other details of new annotation json file
  # new_anno_json['images'] = done
  # new_anno_json['annotations'] = done
  new_anno_json['categories'] = common_cat
  new_anno_json['licenses'] = [{"name":"",
                                "id": 0,
                                "url":""
                                }]
  new_anno_json['info'] = {"contributor":"",
                           "date_created": datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
                           "description": "",
                           "url": "",
                           "version": "",
                           "year": datetime.datetime.now().strftime('%Y')
                           }
  print("[%s] anno json saving" % datetime.datetime.now().strftime('%H:%M:%S'))
  # TODO
  # dummy info fill
  # license stacking
  tp_anno_file = tp_anno / "instances_default.json"
  with open(tp_anno_file, 'w') as f:
    json.dump(new_anno_json, f)
  print("[%s] anno json saved" % datetime.datetime.now().strftime('%H:%M:%S'))
  #make new tsr
  print("[%s] new tsr make" % datetime.datetime.now().strftime('%H:%M:%S'))
  ntsr_table = TSR(Path(t_dir))
  print("[%s] new tsr make done" % datetime.datetime.now().strftime('%H:%M:%S'))
  #pdb.set_trace()
  tt_pkl = Path(t_dir) / "db_table.pkl"
  with open(tt_pkl, 'wb') as f:
    pickle.dump(ntsr_table, f) # save TSR class
  return ntsr_table

def update():
  '''
  update(s_dir, t_dir):
    :return: ?
    Almost same to migrate but here open the t_dir TSR table and update new data with checking file exist
    (if exist -> pass, if not -> add)
    !Warning! This can make duplicate case
  '''
  pass

def includer(elem):
  '''
  includer(elem):
    :return: lambda
    elem: the labels which be included
  '''
  return lambda x: True if x in elem else False

def excluder(elem):
  '''
  excluder(elem):
    :return: lambda
    elem: the labels which be excluded
  '''
  return lambda x: False if x in elem else True


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="TSR db manager")
  parser.add_argument('command', choices=['migrate', 'update', 'extract', 'stat_only'],metavar='command', type=str, help="Among \"migrate, update, extract, stat_only\", choose command what you want to do")
  parser.add_argument('-s','--sdir', metavar='PATH', type=str, help="source directory")
  parser.add_argument('-t','--tdir', metavar='PATH', type=str, help="target directory")
  parser.add_argument('-i','--include', metavar='LABEL', type=str, nargs='+', help="including conditions for filtering. divide as space")
  parser.add_argument('-x','--exclude', metavar='LABEL', type=str, nargs='+', help="excluding conditions for filtering. divide as space")

  args = parser.parse_args()
#  print(args.accumulate(args.integers))

  ###############################################
  #### commands                              ####
  ###############################################
  if args.command == "migrate":
    # option --sdir, tdir check
    if args.sdir == None:
      if yntest("* command \"migrate\" require --sdir. continue as default? [default=./results] *", "[Y/n]"):
        args.sdir = "./results"
        print("-> sdir = %s" % args.sdir)
      else:
        print("** sdir is not decided -> abort **")
        exit(0)
    if args.tdir == None:
      if yntest("* command \"migrate\" require --tdir. continue as default? [default=./tsr] *", "[Y/n]"):
        args.tdir = "./tsr"
        print("-> tdir = %s" % args.tdir)
      else:
        print("** tdir is not decided -> abort **")
        exit(0)
    ntsr = migrate(args.sdir, args.tdir)
    if ntsr == None:
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
      if yntest("* command \"extract\" require --sdir. continue as default? [default=./tsr] *", "[Y/n]"):
        args.sdir = "./tsr"
        print("-> sdir = %s" % args.sdir)
      else:
        print("** sdir is not decided -> abort **")
        exit(0)
    if args.tdir == None:
      if yntest("* command \"extract\" require --tdir. continue as default? [default=./tsr_ex] *", "[Y/n]"):
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
      ext = includer(args.include)
    elif args.exclude != None:
      ext = excluder(args.exclude)
    ntsr = migrate(args.sdir, args.tdir, extractor = ext)
    if ntsr == None:
      print("** the migration ended abnormally, please refer the error code **")
      exit(0)
    # TODO adv extractor - handle label and attribute too
    #                      suggest) read selection file (ex. --extract-file stop_sign.config) composed to some formatted context
  elif args.command == "stat_only":
    # option --sdir only
    if args.sdir == None:
      if yntest("* command \"stat_only\" require --sdir. continue as default? [default=./tsr] *", "[Y/n]"):
        args.sdir = "./tsr"
        print("-> sdir = %s" % args.sdir)
      else:
        print("** sdir is not decided -> abort **")
        exit(0)

    # json exist test
    st_json = Path(args.sdir) / "db_table.json"
    if st_json.exists():
      # s_dir table load
      with open(st_json, 'r') as f:
        tsr_table_old = json.load(f)
        # TODO : json_decoder
        #tsr_table_old = json.load(f, object_hook = json_decoder)
        # This json loading without object_hook(json_decoder),
        # just load the data from json and make a "dict" type
        # In order to get a whole TSR class type object,
        # the each classes (TSR, Project, Task) should be implemented
        # with some constructor which can get the data from dictionary
      #print(tsr_table_old)
      # Because of above issue, the printing is dirty
      # we cannot use the __repr__ functions of each classes
      # Temporary print below
      for k in tsr_table_old:
        if 'plist' in k:
          print(k)
          for p in tsr_table_old[k]:
            for k1 in p:
              if 'task_list' in k1:
                print('\t',k1)
                for t in p[k1]:
                  for k2 in t:
                    if 'image_files' in k2:
                      print('\t\t',k2)
                    else:
                      print('\t\t',k2,t[k2])
              else:
                print('\t',k1,':',p[k1])
        else:
          print(k,':',tsr_table_old[k])

      pdb.set_trace()
      # ask whether renew the table json
      if yntest("* s_dir db_table.json file already exist. Do you want to renew the db_table.json? *", "[y/N]"):
        pass
      else:
        print("** s_dir db_table.json already exist -> abort **")
        exit(0)
    #s_dir table create
    #print("* s_dir db_table.pkl file is not exist -> make new TSR & save pkl")
    tsr_table = TSR(Path(args.sdir))
    #s_dir table save
    with open(st_json, 'w') as f:
      pdb.set_trace()
      json.dump(tsr_table, f, indent=4, default=json_encoder, ensure_ascii=False)
  else:
    args.__repr__()
