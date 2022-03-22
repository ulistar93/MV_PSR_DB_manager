#!/usr/bin/env python3

import json
from pathlib import Path
import pandas as pd
import datetime
import time
import random
import shutil
import pdb
import re
import difflib
from pycocotools.coco import COCO
import pdb

#from pytools.uinputs import Input
#from pytools import tsr
#from pytools import db

def filter(ps, annos, args):
  anno = ''
  if isinstance(annos, list):
    while anno == '':
      if len(annos) > 1:
        print("** filter requires a single annotation file only **")
        print("* please select one annotaion file as \'anno\'")
        print("* or reduce the number of annos member")
        pdb.set_trace()
      else:
        anno = annos[0]
  elif isinstance(annos, str):
    anno = annos
  if len(args) < 1:
    print("** filter requires a output_annotation file name as args **")
    print("* current dir:%s"%ps.resolve())
    pdb.set_trace()
    out_anno_file = input("out_anno_file:")
  else:
    out_anno_file = args[0]

  print('load coco...')
  coco = COCO(anno)

  if len(args) < 2:
    print("** there are no filtering categories **")
    for k in coco.cats.keys():
      print(coco.cats[k])
    nums_str = input("type category numbers:")
    catIds = list(map(int, nums_str.strip().split(' ')))
  else:
    catIds = list(map(int, args[1:]))

  #print('getCatIds...(filtering)')
  #catIds = coco.getCatIds(catNms=['cell phone'])
  print('loadImgs...')
  imgIds = coco.getImgIds(catIds=catIds)
  new_imgs = coco.loadImgs(imgIds)
  print('loadAnns...')
  annIds = coco.getAnnIds(catIds=catIds)
  new_anns = coco.loadAnns(annIds)

  with open(anno, 'r') as f:
    anno_js = json.load(f)
    new_info = anno_js['info']
    new_licen = anno_js['licenses']
    new_cat = anno_js['categories']
  new_anno_dict = {'info':new_info,
                   'licenses':new_licen,
                   'images':new_imgs,
                   'annotations':new_anns,
                   'categories':new_cat}
  print('json.dump...')
  with open(out_anno_file, 'w') as fo:
    json.dump(new_anno_dict, fo)
  print('filter done')
  return

def merge(ps, annos, args):
  if len(annos) < 2:
    print("** merge require at least more than 2 annotation files **")
    return
  if len(args) < 1:
    print("** merge requires a output_annotation file name as args **")
    print("* current dir:%s"%ps.resolve())
    pdb.set_trace()
    out_anno_file = input("out_anno_file:")
  else:
    out_anno_file = args[0]

  all_licenses = [{'name': '', 'id': 0, 'url': ''}]
  all_info = {'contributor': '',
              'date_created': int(time.time()),
              'description': '',
              'url': '',
              'version': '',
              'year': ''}
  all_categories = []
  all_images = []
  all_annotations = []

  all_images_map = {}
  img_name_gidx_map = {}
  cat_name_gidx_map = {}
  anno_g_id = 1
  img_g_idx = 0
  #img_g_id = img_g_idx + 1
  cat_g_idx = 0
  #cat_g_id = cat_g_idx + 1
  for anno in annos:
    print("... read annos %s read "% anno)
    imgId_absimg_map_an = {}
    catId_name_map_an = {}
    with open(anno, 'r') as f:
      anno_js = json.load(f)
      imgdir_prefix = ''
      for img in anno_js['images']:
        abs_img_name = imgdir_prefix + img['file_name']
        if abs_img_name not in img_name_gidx_map.keys():
          while not (ps / abs_img_name).is_file():
            print("* image not found %s *" % abs_img_name)
            print("* please add prefix (ex, train2017/) to image file directory *")
            print("* current_path: %s *" % ps.resolve())
            #pdb.set_trace()
            imgdir_prefix = input("prefix:")
            abs_img_name = imgdir_prefix + img['file_name']
          img_name_gidx_map[abs_img_name] = img_g_idx
          img_g_idx += 1
          all_images.append({'id':img_g_idx,
                             'width':img['width'],
                             'height':img['height'],
                             'file_name':abs_img_name,
                             'license':0,
                             'flickr_url':img['flickr_url'],
                             'coco_url':img['coco_url'],
                             'date_captured':img['date_captured']})
          print('img',img, ' -> id:%d'%img_g_idx)
        imgId_absimg_map_an[img['id']] = abs_img_name
      for cat in anno_js['categories']:
        cat_name = cat['name']
        if cat_name not in cat_name_gidx_map.keys():
          overwirte_cat = False
          overwrite_name = ''
          for candi_cat in list(cat_name_gidx_map.keys()):
            if difflib.SequenceMatcher(a=cat_name, b=candi_cat).ratio() > 0.9:
              print("** there no category %s, but %s is similar **" %(cat_name, candi_cat))
              yn = input("* Do you want to map %s to %s? [y/n]:"%(cat_name, candi_cat))
              overwirte_cat = True if yn == 'y' else False
              if overwirte_cat:
                print("** %d: %s -> %d: %s **" %(cat['id'], cat_name, cat_name_gidx_map[candi_cat]+1, candi_cat))
                overwrite_name = candi_cat
                break
          if overwirte_cat:
            cat_name = overwrite_name
          else:
            cat_name_gidx_map[cat_name] = cat_g_idx
            cat_g_idx += 1
            all_categories.append({'id':cat_g_idx,
                                   'name':cat_name,
                                   'supercategory':''})
            print('cat',cat, ' -> id:%d, name:%s'%(cat_g_idx, cat_name))
        catId_name_map_an[cat['id']] = cat_name
      for ann in anno_js['annotations']:
        new_ann = {'id':anno_g_id,
                   'image_id':img_name_gidx_map[imgId_absimg_map_an[ann['image_id']]],
                   'category_id':cat_name_gidx_map[catId_name_map_an[ann['category_id']]],
                   'segmentation':[],
                   'area': ann['area'],
                   'bbox': ann['bbox'],
                   'iscrowd': ann['iscrowd'],
                   'attributes': ann['attributes']
                   }
        print('ann',ann, ' -> id:%d, image_id:%d, category_id:%d'%(anno_g_id,
                                                             img_name_gidx_map[imgId_absimg_map_an[ann['image_id']]],
                                                             cat_name_gidx_map[catId_name_map_an[ann['category_id']]])
              )
        anno_g_id += 1
        all_annotations.append(new_ann)
      pass
  new_anno_json = {'licenses' : all_licenses,
                   'info' : all_info,
                   'categories' : all_categories,
                   'images' : all_images,
                   'annotations' : all_annotations}
  print('json.dump...')
  with open(out_anno_file, 'w') as fo:
    json.dump(new_anno_json, fo)
  print('merge done')
  return

def migrate(s_db, t_dir, extractors=[], tv_file=None, tv_ratio=1.0, renameTF=True):
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
  def lprint(_str):
    _str = str(_str)
    dt = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    print("[%s migrate] " % dt + _str)

  if s_db.amiex: # if s_db is ex_db
    #pdb.set_trace()
    lprint("** ex_db cannot be the source of migration -> make new db.pkl **")
    s_db = db.DB(s_db.sdir)
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
    lprint("* t_dir %s is not exist -> make a new dir *" % t_dir)
    tp.mkdir(parents=True, exist_ok=True)
    pass
  elif not tp.is_dir():
    lprint("** t_dir %s exist but not a dir -> abort **" % t_dir)
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

  lprint("* %s db copy to %s ex_db *"%(s_db.sdir, t_dir))
  ex_db = s_db.copy()
  ex_db.sdir = t_dir
  ex_db.amiex = True
  for ext in extractors:
    lprint("* %s extractor %s-clude %s *" %(ext[0],ext[1], str(ext[2:])))
    ex_db.extract(ext)

  ####################################
  # 3) sorting and setting ex_db
  #    include train/valid devider
  ####################################
  # set global id of img_df
  lprint("* set global id of img_df *")
  total_num_img_copy = len(ex_db.img_df)
  ex_db.img_df['new_id'] = list(range(1,total_num_img_copy+1))
  ex_db.anno_df['new_id'] = list(range(1,len(ex_db.anno_df)+1))
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

  lprint("* make common_cat *")
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

  lprint("* train/valid devide *")
  # train/valid devide
  #total_num_img_copy = len(ex_db.img_df) #done above
  if tv_file != None:
    with open(tv_file,'r') as f:
      tv_tlist = []
      tv_vlist = []
      train_st = False
      valid_st = False
      for line in f:
        if not train_st and not valid_st:
          if "[train]" in line:
            train_st = True
          elif "[valid]" in line:
            valid_st = True
        elif train_st:
          if "[valid]" in line:
            valid_st = True
            train_st = False
            continue
          elif '-' in line:
            _s, _e = line.strip().split('-')
            tv_tlist += [ str(i).zfill(len(_s)) for i in range(int(_s), int(_e)+1) ]
          elif 'else' in line:
            else_incl_list = tv_tlist
          else: # just number
            tv_tlist.append(line)
        elif valid_st:
          if "[train]" in line:
            valid_st = False
            train_st = True
            continue
          elif '-' in line:
            _s, _e = line.strip().split('-')
            tv_vlist += [ str(i).zfill(len(_s)) for i in range(int(_s), int(_e)+1) ]
          elif 'else' in line:
            else_incl_list = tv_vlist
          else: # just number
            tv_vlist.append(line)
    #pdb.set_trace()
    if else_incl_list == tv_tlist:
      sel_list = tv_vlist
      sel_tv = False
    else:
      sel_list = tv_tlist
      sel_tv = True
    #pdb.set_trace()
    ex_db.img_df['tv'] = ex_db.img_df['file_name'].map(lambda x : sel_tv if x.split('/')[-1].split('.')[0] in sel_list else not sel_tv)
  elif tv_ratio == 1:
    # no valid
    tv_ticket = [True] * total_num_img_copy
    ex_db.img_df['tv'] = tv_ticket
  elif tv_ratio == 0:
    # no train
    tv_ticket = [False] * total_num_img_copy
    ex_db.img_df['tv'] = tv_ticket
  else:
    #tv_ticket = random_ticket(total_num_img_copy, tv_ratio)
    tv_ticket_idx = list(range(total_num_img_copy)) # 0 ~ n-1
    random.shuffle(tv_ticket_idx)
    #tv_ticket = [ True for x in tv_ticket_idx if x <= (tv_ratio * (total_num_img_copy -1)) else False ]
    tv_ticket = [ True if x <= (tv_ratio * (total_num_img_copy -1)) else False for x in tv_ticket_idx ]
    ex_db.img_df['tv'] = tv_ticket
    #  train   val
    # |<----->|<->|
    # 0       |  n-1
    #         x = (n-1)*r
    # so that,
    # (n-1)*r : (n-1) - (n-1)r
    # = r : 1-r
  #ex_db.img_df['tv'] = tv_ticket
  #pdb.set_trace()
  ex_db.anno_df['tv'] = ex_db.anno_df['new_image_id'].map(lambda x : ex_db.img_df[ex_db.img_df['new_id']==x]['tv'].values[0])

  lprint("* set img new_file_name *")
  # renameTF = True -> numbered name
  # renameTF = False -> orginal name
  # renameTF = True is default 
  rename_len = len(str(total_num_img_copy)) + 1
  def rename_img_file_name(df):
    _fname = df['file_name'].split('.')
    _format = _fname[-1]
    _name = '.'.join(_fname[:-1]).split('/')[-1]
    _new_id = df['new_id']
    new_name = ''
    if renameTF:
      new_name = str(_new_id).zfill(rename_len) + '.' + _format
    else: #renameTF = False
      #new_name = re.sub('[^a-zA-Z0-9_/\-]','', _name)
      #new_name = new_name.replace('-','_').replace('/', '-') + '.' + _format
      new_name = _name + '.' + _format
    _tv = df['tv']
    if _tv:
      new_name = 'train/' + new_name
    else:
      new_name = 'valid/' + new_name
    return new_name
  ex_db.img_df['new_file_name'] = ex_db.img_df.apply(rename_img_file_name, axis=1)
  #ex_db.img_df['new_file_name_only'] = ex_db.img_df.apply(rename_img_file_name, axis=1)
  #ex_db.img_df['new_file_name'] = ex_db.img_df.apply(lambda x: 'train/'+x['new_file_name_only'] if x.tv else 'valid/'+x['new_file_name_only'], axis=1)

  #tp = Path(t_dir) #done above
  tp_pj_task_name = "project_0/task_0"
  tp_anno = tp / tp_pj_task_name / "annotations"
  tp_anno.mkdir(parents=True)

  tp_image = tp / tp_pj_task_name / "images"
  tp_image_trn = tp_image / "train"
  tp_image_val = tp_image / "valid"
  tp_image_trn.mkdir(parents=True, exist_ok=True)
  tp_image_val.mkdir(parents=True, exist_ok=True)

  lprint("* set new_full_path *")
#  def new_full_path(df):
#    _tv = df['tv']
#    _new_name = df['new_file_name']
#    #_new_name = df['new_file_name_only']
#    if _tv:
#      return tp_image_trn / _new_name
#    else:
#      return tp_image_val / _new_name
#  ex_db.img_df['new_full_path'] = ex_db.img_df.apply(new_full_path, axis=1)
  #ex_db.img_df['new_full_path'] = ex_db.img_df['new_file_name'].map(lambda x: tp_image / x, axis=1)
  ex_db.img_df['new_full_path'] = ex_db.img_df['new_file_name'].map(lambda x: tp_image / x)

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

  lprint("* make dict for anno_json *")
  for _, im in ex_db.img_df.iterrows():
    if im.tv:
      _an_json = new_trn_anno_json
    else:
      _an_json = new_val_anno_json
    _an_json['images'].append({"id":im.new_id,
                               "width":im.width,
                               "height":im.height,
                               "file_name":im.new_file_name,
                               "license":im.license,
                               "flicker_url":"",
                               "coco_url":"",
                               "date_captured":im.date_captured
                               })
  for _, an in ex_db.anno_df.iterrows():
    if an.tv:
      _an_json = new_trn_anno_json
    else:
      _an_json = new_val_anno_json
    _an_json['annotations'].append({"id":an.new_id,
                                    "image_id":an.new_image_id,
                                    "category_id":an.common_cat_id,
                                    "segmentation":an.segmentation,
                                    "area":an.area,
                                    "bbox":an.bbox,
                                    "iscrowd":an.iscrowd,
                                    "attributes":an.attributes
                                    })

  lprint("* copy img file start *")
  #pdb.set_trace()
  for idx, im in ex_db.img_df.iterrows():
    _org_file = im.full_path
    _new_file = im.new_full_path
    try:
      _info_str = str(_org_file) + " -> " + str(_new_file)
      lprint("(%d/%d) cp "%(idx,total_num_img_copy) + _info_str )
      shutil.copyfile(_org_file, _new_file)
    except:
      lprint("** shutil.copy sth wrong **")
      pdb.set_trace()

  lprint("* anno file save *")
  trn_anno_file = tp_anno / "instances_train.json"
  val_anno_file = tp_anno / "instances_valid.json"
  if new_trn_anno_json['images']: # if not empty
    with open(trn_anno_file, 'w') as f:
      json.dump(new_trn_anno_json, f, sort_keys=True)
  if new_val_anno_json['images']: # if not empty
    with open(val_anno_file, 'w') as f:
      json.dump(new_val_anno_json, f, sort_keys=True)
  ex_db.anno_flist.append(trn_anno_file)
  ex_db.anno_flist.append(val_anno_file)

  lprint("* ex_db pickel save *")
  ex_db.save_pkl(tp / "ex_db.pkl")
  return ex_db

