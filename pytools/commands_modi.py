#!/usr/bin/env python3

import json
from pathlib import Path
import datetime
import shutil
import pdb

from pytools.uinputs import Input
from pytools import tsr
#from pytools import db

def migrate(s_dir, t_dir, extractor=None, tv_ratio=1.0, renameTF=True):
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
  # train data ratio per the whole dataset

  # 0) function argument check (s_dir, t_dir)
  # t_dir empty check
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
    if not Input('yn',"* t_dir %s exist but not emtpy -> please use \"update\" *\n* do you want to *DELETE* all and make a new ? *" % t_dir, "[y/N]"):
      return None
    else: # continue
      shutil.rmtree(tp)
      tp.mkdir()
      pass

  # s_dir exist check
  sp = Path(s_dir)
  if not sp.exists():
    print("** the s_dir %s is not exist -> abort **" % s_dir)
    return None

  # 1) Read s_dir (load or gen new tsr_table.json)
  # s_dir tsr_table check
  print("[%s] s_dir table file check" % datetime.datetime.now().strftime('%H:%M:%S'))
  st_json = Path(s_dir) / "db_table.json"
  if st_json.exists():
    # load
    print("* s_dir db_table.json file already exist -> load db_table.json *")
    with open(st_json, 'r') as f:
      tsr_table_json = json.load(f) # load tsr json
    tsr_table = tsr.TSR(tsr_table_json) # make tsr class from json
  else:
    # create
    print("* s_dir db_table.json file is not exist -> make new TSR & save json")
    tsr_table = tsr.TSR(Path(s_dir))
    with open(st_json, 'w') as f:
      json.dump(tsr_table, f, indent=4, default=tsr.json_encoder, ensure_ascii=False, sort_keys=True) #save json
  print("[%s] do copy and gen tdir" % datetime.datetime.now().strftime('%H:%M:%S'))
  print("[%s] %d Project / %d tasks in sdir" % (datetime.datetime.now().strftime('%H:%M:%S'),len(tsr_table.plist), sum(list(len(p.task_list) for p in tsr_table.plist))))

  # 2) copy data at target directory
  # utils #
  def categories_cmp(cm, an):
    '''
    return (1) dictionary which id(int) to id(int)
           (2) list of dictionaries which have the detail info for each categories
    '''
    res_dict = {}
    info_dict = []
    for cat_an in an:
      _name = cat_an['name']
      s_id = cat_an['id']
      t_id = 0
      if extractor(_name): # True = to be include
        for cat_cm in cm:
          if _name == cat_cm['name']:
            t_id = cat_cm['id']
            break
        if t_id == 0:
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
      info_dict.append({"name":_name, "id_change":"%d->%d"%(s_id, t_id)})
    return res_dict, info_dict

  total_num_img = 0
  for p in tsr_table.plist:
    for t in p.task_list:
      total_num_img += len(t["num_image"])

  def static_vars(**kwargs):
    def decorate(func):
      for k in kwargs:
        setattr(func,k,kwargs[k])
      return func
    return decorate
  _t_tickets = int(p*total_num_img)
  _f_tickets = total_num_img - _t_tickets

  # p would be same to True ratio of returns
  @static_vars(p=tv_ratio,t_tickets=_t_tickets, f_tickets=_f_tickets)
  def tv_ratio_devider():
    '''
    return True if Training
           False if Validation
    * Caution * before to use please set attribute "t_tickets" and "f_tickets"
    '''
    if (tv_ratio_devider.t_tickets + tv_ratio_devider.f_tickets) == 0:
      raise ValueError("tv_ratio_devider sold out all tickets")
      pdb.set_trace()
    elif tv_ratio_devider.t_tickets == 0:
      tv_ratio_devider.f_tickets -= 1
      return False
    elif tv_ratio_devider.f_tickets == 0:
      tv_ratio_devider.t_tickets -= 1
      return True
    elif random.random() <= p:
      tv_ratio_devider.t_tickets -= 1
      return True
    else:
      tv_ratio_devider.f_tickets -= 1
      return False

  #def tv_selective_devider(key):
    # TODO - This might be need in case when we want to select some folders as validation
    # for example, "Kaggle" or "Chile" can be validation set and others as Training

  # set target dir(path) names#
  #tp = Path(t_dir) #done above
  tp_pj_task_name = "project_0/task_0"
  tp_pj = tp / "project_0"
  tp_task = tp_pj / "task_0"
  tp_anno = tp_task / "annotations"
  tp_image = tp_task / "images"
  tp_image_trn = tp_image / "train"
  tp_image_val = tp_image / "valid"
  tp_anno.mkdir(parents=True)
  tp_image_trn.mkdir(parents=True, exist_ok=True)
  tp_image_val.mkdir(parents=True, exist_ok=True)
  common_cat = []
  #new_anno_json = {'images':[],
  new_trn_anno_json = {'images':[],
                       'annotaions':[],
                       'categories':[],
                       'licenses':[],
                       'info':{}
                       }
  new_val_anno_json = {'images':[],
                       'annotaions':[],
                       'categories':[],
                       'licenses':[],
                       'info':{}
                       }
  #new_val_anno_json['images'] = []
  #new_val_anno_json['annotations'] = []
  #new_val_anno_json = {'images':[], 'annotations':[]}

  g_img_id = 0
  g_anno_id = 0
  # for project
  #   for task
  #     0) categories check
  #     1) do migration (copy images)
  #     2) make other annotation detail
  # vs
  #     0) categories check
  #     1) read dir & make migration list
  #     2) do migration (copy images)
  #     3) make other annotation detail
  all_migration_info = {} # {project{task[cat_id_map, img_id_map]}}
  all_migration_info['project_info'] = []
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
      ###################################################################
      ## anno file loop ##
      ####################
      # for each annotation file, 
      for anno_file in t.anno_files:
        with open(anno_file, 'r') as f:
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
            new_name = org_name if (renameTF == False) or (t.shortname == '') else new_name = t.shortname + '_' + str(l_img_id) + '.' + file_format
            # when renameTF = False -> org_name
            # when renameTF = True, but they have no new shortname -> org_name
            # else rename
            new_file = tp_image_trn / new_name if tv_ratio_devider() else tp_image_val / new_name
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

#############################################################################
            # TODO - HERE 2021.08.24 Before Vacation
            # to set annotaiton json files for each train and valid
#############################################################################

            if 'train' in new_file:
              new_anno_json = new_trn_anno_json
            elif 'valid' in new_file:
              new_anno_json = new_val_anno_json
            new_anno_json['images'].append({ "id": g_img_id,
                                            "width": img["width"],
                                            "height": img["height"],
                                            "license": img["license"],
                                            #"file_name": tp_pj_task_name+'/images/'+new_name,
                                            "file_name": str(new_file),
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
      # end for anno_files:
    # end for task_list:
    all_migration_info['project_info'].append(project_mapping_info)
  # end for tsr_table.plist:



  tp_info = tp / "migration_info.json"
  with open(tp_info, 'w') as f:
    json.dump(all_migration_info, f, ensure_ascii=False, sort_keys=True, indent=4)

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
  #tp_anno_file = tp_anno / "instances_default.json"
  trn_anno_file = tp_anno / "instances_trainTSR.json" # TODO
  val_anno_file = tp_anno / "instances_valTSR.json" # TODO devide train/val annotations
  with open(tp_anno_file, 'w') as f:
    json.dump(new_anno_json, f, sort_keys=True)
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

