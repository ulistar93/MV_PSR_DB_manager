#!/usr/bin/env python3

import json
from pathlib import Path
import pandas as pd
import datetime
import random
import shutil
import pdb

from pytools.uinputs import Input
from pytools import tsr
from pytools import db

#def migrate(s_dir, t_dir, extractor=None, tv_ratio=1.0, renameTF=True):
#def migrate(s_db, t_dir, extractor=None, tv_ratio=1.0, renameTF=True):
def migrate(s_db, t_dir, extractors=[], tv_ratio=1.0, renameTF=True):
  '''
  - TODO -
  migrate(s_db, t_dir):
  - OLD -
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
  # utils #
  def categories_cmp(cm, an, ext):
    '''
    return (1) dictionary which id(int) to id(int)
           (2) list of dictionaries which have the detail info for each categories
    '''
    res_dict = {}
    info_list = []
    for cat_an in an:
      _name = cat_an['name']
      s_id = cat_an['id']
      t_id = 0
      if ext(_name): # True = to be include
        for cat_cm in cm:
          if _name == cat_cm['name']:
            t_id = cat_cm['id']
            break
        if t_id == 0: # if there is no name-matched category in cm(common_cat)
          max_t_id = max([ x['id'] for x in cm]) if cm else 0 #if not empty -> max
          t_id = max_t_id + 1
          cm.append({"id": t_id,
                     "name": _name,
                     "supercategory":""
                     })
          # extend always
      else: # excluded label -> skipping
        pass # keep t_id = 0
      res_dict[s_id] = t_id
      info_list.append({"name":_name, "id_change":"%d->%d"%(s_id, t_id)})
    return res_dict, info_list

  #######################
  # 
  # 0) directory check (s_dir, t_dir)
  # 1) read org data (s_dir)
  # 2) make copy candidate list <- apply extractor
  # 3) mapping org to target dir <- apply devider
  # 3-2) set migration info
  # 4) real copy file
  #
  #########################

  #########################
  # 0) directory check (s_dir, t_dir)
  #########################
  # t_dir empty check
  tp = Path(t_dir)
  if not tp.exists():
    print("* t_dir %s is not exist -> make a new dir *" % t_dir)
    tp.mkdir(parents=True, exist_ok=True)
    pass
  elif not tp.is_dir():
    print("** t_dir %s exist but not a dir -> abort **" % t_dir)
    return None
  elif len(list(tp.iterdir())) > 0:
    #tdir is alread exist and not empty
    if not Input('yn',"* t_dir %s exist but not emtpy -> please use \"update\" *\n* do you want to *DELETE* all and make a new ? *" % t_dir, "[y/N]"):
      return None
    else: # continue
      shutil.rmtree(tp)
      tp.mkdir(parents=True, exist_ok=True)
      pass

  #########################
  # 1) read org data -> s_db
  #########################

  #########################
  # 2) make copy candidate list <- apply extractor
  #########################
  #if extractor == None:
  #  extractor = lambda x : True

  ex_db = s_db.copy()
  for ext in extractors:
    ex_db.extract(ext)

##############################################
## TODO - HERE 
## 3) make a plan to copy by using ex_db
##    include train/valid devider
##############################################

  pdb.set_trace()
  pass
  #########################
  # 3) mapping org to target dir <- apply devider
  #########################
  #tp = Path(t_dir) #done above
  tp_pj_task_name = "project_0/task_0"
  tp_anno = tp / tp_pj_task_name / "annotations"
  tp_anno.mkdir(parents=True)
  tp_image = tp / tp_pj_task_name / "images"
  tp_image_trn = tp_image / "train"
  tp_image_val = tp_image / "valid"
  tp_image_trn.mkdir(parents=True, exist_ok=True)
  tp_image_val.mkdir(parents=True, exist_ok=True)
  new_trn_anno_json = {'images':[],
                       'annotations':[],
                       'categories':[],
                       'licenses':[],
                       'info':{}
                       }
  new_val_anno_json = {'images':[],
                       'annotations':[],
                       'categories':[],
                       'licenses':[],
                       'info':{}
                       }

  total_num_img_copy = len(img_copy_list)
  tv_ticket = []
  if tv_ratio == 1:
    # no valid
    tv_ticket = [True] * total_num_img_copy
  elif tv_ratio == 0:
    # no train
    tv_ticket = [False] * total_num_img_copy
  else:
    #tv_ticket = random_ticket(total_num_img_copy, tv_ratio)
    tv_ticket_idx = list(range(total_num_img_copy)) # 0 ~ n-1
    random.shuffle(tv_ticket_idx)
    #tv_ticket = [ True for x in tv_ticket_idx if x <= (tv_ratio * (total_num_img_copy -1)) else False ]
    tv_ticket = [ True if x <= (tv_ratio * (total_num_img_copy -1)) else False for x in tv_ticket_idx ]
    #  train   val
    # |<----->|<->|
    # 0       |  n-1
    #         x = (n-1)*r
    # so that,
    # (n-1)*r : (n-1) - (n-1)r
    # = r : 1-r

  #assert len(tv_ticket) == len(img_copy_list)
  for tv, _img in zip(tv_ticket, img_copy_list):
    if tv: # if train
      _img['new_file'] = tp_image_trn / _img['new_name']
      _img['new_anno_json'] = new_trn_anno_json
    else: # if valid
      _img['new_file'] = tp_image_val / _img['new_name']
      _img['new_anno_json'] = new_val_anno_json
    #########################
    # 3-2) set migration info
    #      TODO - external loop & without list pointer in _img
    #########################
    #for c in _img['t_mig_info_img_map']:
    #  if c == _img['org_file']:
    #    c = c + ' -> ' + str(_img['new_file'])
    #    break

  #########################
  # 4) real copy file
  #########################

  g_anno_id = 1
  for i, _img in enumerate(img_copy_list):
    _org_file = _img['org_file']
    _new_file = _img['new_file']
    _task_info_imgmap = []
    for p_mig_info in migration_info['project_info']:
      for t_mig_info in p_mig_info['task_info']:
        if t_mig_info['org_task_name'] == _img['task_name']:
          _task_info_imgmap = t_mig_info['img_map']
    try:
      _info_str = str(_org_file) + " -> " + str(_new_file)
      _task_info_imgmap.append(_info_str)
      print("  cp", _info_str )
      shutil.copyfile(_org_file, _new_file)
    except:
      print("** shutil.copy sth wrong **")
      pdb.set_trace()
    _img['new_anno_json']['images'].append({ "id": i+1,
                                            "width": _img['img']["width"],
                                            "height": _img['img']["height"],
                                            #"license": _img['img']["license"],
                                            "license": 0,
                                            "file_name": str(_img['new_file']),
                                            "flickr_url": _img['img']["flickr_url"],
                                            "coco_url": _img['img']["coco_url"],
                                            "date_captured": _img['img']["date_captured"]
                                            })
    for an in _img['ans']:
      _img['new_anno_json']['annotations'].append({"id": g_anno_id,
                                                 "image_id": i+1,
                                                 "category_id": _img['new_cat'],
                                                 "segmentation": an['segmentation'],
                                                 "area": an['area'],
                                                 "bbox": an['bbox'],
                                                 "iscrowd": an['iscrowd'],
                                                 "attributes": an['attributes']
                                                 })
      g_anno_id += 1

  # TODO - dummy info fill
  new_trn_anno_json['categories'] = common_cat
  new_val_anno_json['categories'] = common_cat
  new_trn_anno_json['licenses'] = [{"name":"",
                                    "id": 0,
                                    "url":""
                                    }]
  new_val_anno_json['licenses'] = new_trn_anno_json['licenses']
  new_trn_anno_json['info'] = {"contributor":"",
                               "date_created": datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
                               "description": "",
                               "url": "",
                               "version": "",
                               "year": datetime.datetime.now().strftime('%Y')
                               }
  new_val_anno_json['info'] = new_trn_anno_json['info']
  print("[%s] anno json saving" % datetime.datetime.now().strftime('%H:%M:%S'))

  pdb.set_trace()
  trn_anno_file = tp_anno / "instances_train.json"
  val_anno_file = tp_anno / "instances_valid.json"
  if new_trn_anno_json['images']: # if not empty
    with open(trn_anno_file, 'w') as f:
      json.dump(new_trn_anno_json, f, sort_keys=True)
  if new_val_anno_json['images']: # if not empty
    with open(val_anno_file, 'w') as f:
      json.dump(new_val_anno_json, f, sort_keys=True)

  pdb.set_trace()
  tp_info = tp / "migration_info.json"
  with open(tp_info, 'w') as f:
    json.dump(migration_info, f, ensure_ascii=False, sort_keys=True, indent=4)

  print("[%s] anno json saved" % datetime.datetime.now().strftime('%H:%M:%S'))
  #make new tsr
  print("[%s] new tsr make" % datetime.datetime.now().strftime('%H:%M:%S'))
  ntsr_table = tsr.TSR(Path(t_dir))
  print("[%s] new tsr make done" % datetime.datetime.now().strftime('%H:%M:%S'))
  #pdb.set_trace()
  tt_json = Path(t_dir) / "db_table.json"
  with open(tt_json, 'w') as f:
    json.dump(ntsr_table, f, indent=4, default=tsr.json_encoder, ensure_ascii=False, sort_keys=True)
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

#def includer(elem):
#  '''
#  includer(elem):
#    :return: lambda
#    elem: the labels which be included
#  '''
#  return lambda x: True if x in elem else False
#
#def excluder(elem):
#  '''
#  excluder(elem):
#    :return: lambda
#    elem: the labels which be excluded
#  '''
#  return lambda x: False if x in elem else True

