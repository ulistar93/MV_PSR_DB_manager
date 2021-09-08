#!/usr/bin/env python3

import json
from pathlib import Path
import pandas as pd
import datetime
import random
import shutil
import pdb
import re

from pytools.uinputs import Input
from pytools import tsr
from pytools import db

#def migrate(s_dir, t_dir, extractor=None, tv_ratio=1.0, renameTF=True):
#def migrate(s_db, t_dir, extractor=None, tv_ratio=1.0, renameTF=True):
def migrate(s_db, t_dir, extractors=[], tv_ratio=1.0, renameTF=False):
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

  ####################################
  # 3) sorting and setting ex_db
  #    include train/valid devider
  ####################################
  # set global id of img_df
  total_num_img_copy = len(ex_db.img_df)
  ex_db.img_df['new_id'] = list(range(1,total_num_img_copy+1))
  #anno_df_new_img_id = pd.DataFrame()
  anno_df_new_img_id = []
  for anno_file in ex_db.anno_flist:
    _an_df_an = ex_db.anno_df[ex_db.anno_df['anno_file'] == anno_file]
    _im_df_an = ex_db.img_df[ex_db.img_df['anno_file'] == anno_file]
    #def get_new_img_id(old_img_id):
    #  return int(_im_df_an[_im_df_an['id']==old_img_id]['new_id'])
    #_an_df_an['new_img_id'] = _an_df_an['image_id'].map(get_new_img_id)
    #_an_df_an['new_image_id'] = _an_df_an['image_id'].map(lambda x : int(_im_df_an[_im_df_an['id']==x]['new_id']))
    #anno_df_new_img_id = anno_df_new_img_id.append(_an_df_an)
    anno_df_new_img_id += list(_an_df_an['image_id'].map(lambda x : int(_im_df_an[_im_df_an['id']==x]['new_id'])))
  #ex_db.anno_df = anno_df_new_img_id
  ex_db.anno_df['new_image_id'] = anno_df_new_img_id

  # ex_db.cat_df reducing -> make common_cat
  common_cat = []
  common_cat_map = {}
  for idx, ct in ex_db.cat_df.iterrows():
    if ct['name'] not in common_cat_map.keys():
      cc_id = ct['id']
      while cc_id in common_cat_map.values():
        cc_id += 1
      common_cat_map[ct['name']] = cc_id
      common_cat.append({"id":cc_id,
                         "name":ct['name'],
                         "supercategory":ct['supercategory']
                         })
  ex_db.cat_df['common_cat_id'] = ex_db.cat_df['name'].map(lambda x: common_cat_map[x])

  anno_df_common_cat_id = []
  for anno_file in ex_db.anno_flist:
    _an_df_an = ex_db.anno_df[ex_db.anno_df['anno_file'] == anno_file]
    _ct_df_an = ex_db.cat_df[ex_db.cat_df['anno_file'] == anno_file]
    cc_map = {}
    for _, c in _ct_df_an.iterrows():
      cc_map[c['id']] = c['common_cat_id']
    anno_df_common_cat_id += list(_an_df_an['category_id'].map(lambda x : cc_map[x]))
  ex_db.anno_df['common_cat_id'] = anno_df_common_cat_id

  #################################################
  ## memo : new_image_id 를 db.py로 넣으려했는데, 생각해보니 extractor 가 없을 경우 실행이 안될듯
  ##        여기서 extract 다 끝나고 하는게 맞는듯
  #################################################

  # train/valid devide
  #total_num_img_copy = len(ex_db.img_df) #done above
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
  ex_db.img_df['tv'] = tv_ticket
  ex_db.anno_df['tv'] = ex_db.anno_df['new_image_id'].map(lambda x : ex_db.img_df[ex_db.img_df['new_id']==x]['tv'].values[0])

  #renameTF = False -> shrinked name
  #renameTF = True -> numbered name
  rename_len = len(str(total_num_img_copy)) + 1
  def rename_img_file_name(df):
    _fname = df['file_name'].split('.')
    _name = '_'.join(_fname[:-1])
    _format = _fname[-1]
    _new_id = df['new_id']
    new_name = ''
    if renameTF:
      new_name = str(_new_id).zfill(rename_len) + '.' + _format
    else: #renameTF = False
      new_name = re.sub('[^a-zA-Z0-9_/\-]','', _name)
      new_name = new_name.replace('-','_').replace('/', '-') + '.' + _format
    return new_name
  ex_db.img_df['new_file_name'] = ex_db.img_df.apply(rename_img_file_name, axis=1)

  #tp = Path(t_dir) #done above
  tp_pj_task_name = "project_0/task_0"
  tp_anno = tp / tp_pj_task_name / "annotations"
  tp_anno.mkdir(parents=True)
  trn_anno_file = tp_anno / "instances_train.json"
  val_anno_file = tp_anno / "instances_valid.json"

  tp_image = tp / tp_pj_task_name / "images"
  tp_image_trn = tp_image / "train"
  tp_image_val = tp_image / "valid"
  tp_image_trn.mkdir(parents=True, exist_ok=True)
  tp_image_val.mkdir(parents=True, exist_ok=True)

  pdb.set_trace()
  ex_db.img_df['new_anno_file'] = ex_db.img_df['tv'].map(lambda x: trn_anno_file if x == 'train' else val_anno_file )
  ex_db.anno_df['new_anno_file'] = ex_db.anno_df['tv'].map(lambda x: trn_anno_file if x == 'train' else val_anno_file )
  pdb.set_trace()
  # file이름으로 하는게 맞나? json으로 하는게 맞나?
  def new_full_path(df):
    _tv = df['tv']
    _new_name = df['new_file_name']
    if _tv:
      return tp_image_trn / _new_name
    else:
      return tp_image_val / _new_name
  ex_db.img_df['new_full_path'] = ex_db.img_df.apply(new_full_path, axis=1)
  pdb.set_trace()

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
  new_trn_anno_json['licenses'] = [{"name":"",
                                    "id": 0,
                                    "url":""
                                    }]
  new_val_anno_json['licenses'] = [{"name":"",
                                    "id": 0,
                                    "url":""
                                    }]
  time_now = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
  new_trn_anno_json['info'] = {"contributor":"",
                               "date_created": time_now,
                               "description": "",
                               "url": "",
                               "version": "",
                               "year": datetime.datetime.now().strftime('%Y')
                               }
  new_val_anno_json['info'] = {"contributor":"",
                               "date_created": time_now,
                               "description": "",
                               "url": "",
                               "version": "",
                               "year": datetime.datetime.now().strftime('%Y')
                               }
  new_trn_anno_json['categories'] = common_cat
  new_val_anno_json['categories'] = common_cat
  ################################
  # TODO - HERE 2021.09.08
  #       devide dataframe
  #       make dict for anno_json
  #       copy img file
  ################################
  #trn_img_df = ex_db.img_df[]
  #new_trn_anno_json['images'] = 

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

