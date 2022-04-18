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

def tv_divide(img_num, tv_ratio, tv_conut_mode, tv_count):
  # (int, tuple(float,float), True/False, tuple(int,int))
  random_extract_val = True
  if tv_conut_mode:
    while img_num != (tv_count[0] + tv_count[1]):
      print("** train/val divide by img count, but the sum is not match **")
      print("* please macth the below values to be img_num = sum(tv_count)*")
      print("* img_num=%d, tv_count=(train,val)=(%d,%d) *")
      pdb.set_trace()
  else:
    t_val = round(tv_ratio[0] * img_num)
    v_val = round(tv_ratio[1] * img_num)
    t_val += img_num - t_val - v_val
    tv_count = (t_val, v_val)
  tv_list = ['train'] * t_val + ['val'] * v_val
  if random_extract_val:
    random.shuffle(tv_list)
  return tv_list

def filter(ps, annos, args):
  # annos = [anno_file, ...]
  out_anno_files = []
  if isinstance(annos, str):
    annos = [annos]
    if len(args) < 1:
      print("** when filter a single file, **")
      print("** it requires a single output annotation file name **")
      print("* current dir:%s"%ps.resolve())
      pdb.set_trace()
      out_anno_file = input("out_anno_file:")
    else:
      out_anno_file = args[0]
    if '.json' not in out_anno_file:
      out_anno_file += '.json'
    out_anno_files.append(out_anno_file)
  elif isinstance(annos, list):
    if len(args) < 1:
      print("** when filter multiple files, **")
      print("** it requires a postfix tag (include _) **")
      pdb.set_trace()
      out_tags = '_' + input("out_tags:_")
    else:
      out_tags = args[0]
      if '_' != out_tags[0]:
        out_tags = '_' + out_tags
    if '.json' not in out_tags:
      out_tags += '.json'
    out_anno_files = [ an[:-5] + out_tags for an in annos ]

  for n, anno in enumerate(annos):
    anno_file = str((ps / anno).resolve())
    print('load coco... %s' % anno_file)
    coco = COCO(anno_file)

    # get category id for filtering
    if len(args) < 2:
      print("** there are no filtering categories **")
      for k in coco.cats.keys():
        print(coco.cats[k])
      nums_str = input("type category numbers:")
      catIds = list(map(int, nums_str.strip().split(' ')))
    else:
      catIds = list(map(int, args[1:]))

    print('loadImgs...')
    imgIds = coco.getImgIds(catIds=catIds)
    new_imgs = coco.loadImgs(imgIds)
    print('loadAnns...')
    annIds = coco.getAnnIds(catIds=catIds)
    new_anns = coco.loadAnns(annIds)
    new_cat = [coco.cats[c] for c in catIds]
    with open(anno_file, 'r') as f:
      anno_js = json.load(f)
      new_info = anno_js['info']
      new_licen = anno_js['licenses']
    new_anno_dict = {'info':new_info,
                     'licenses':new_licen,
                     'images':new_imgs,
                     'annotations':new_anns,
                     'categories':new_cat}
    print('json.dump... %s'%out_anno_files[n])
    with open(out_anno_files[n], 'w') as fo:
      json.dump(new_anno_dict, fo)
    print('filter done')
  return

def copy(ps, anno, args):
  # read annotation file and copy images to output dir
  # check anno is a single file
  anno_file = str((ps / anno).resolve())
  while not isinstance(anno, str):
    print("** copy requires a single annotation only **")
    print("* please edit anno as a single file name *")
    print("current_path=",ps)
    print("anno=",anno)
    pdb.set_trace()
  if len(args) < 1:
    print("** copy requires a output directory **")
    print("* current dir:%s"%ps.resolve())
    output_dir = input("output_dir:")
  else:
    output_dir = args[0]

  out_path = Path(output_dir)
  print("output_dir: %s" % out_path.resolve())
  img_out_dir = out_path / 'images'
  anno_out_dir = out_path / 'annoatations'
  img_out_dir.mkdir(exist_ok=True, parents=True)
  anno_out_dir.mkdir(exist_ok=True, parents=True)

  tv_ratio = (1.0, 0.0)
  tv_count_mode = False
  tv_count = (0 ,0)
  if len(args) >2:
    # divide training and validation
    t_val = args[1].split('train=')[1]
    v_val = args[2].split('val=')[1]
    if int(t_val)+int(v_val) == 10:
      tv_ratio = ( int(t_val)/10, int(v_val)/10 )
    elif int(t_val)+int(v_val) == 100:
      tv_ratio = ( int(t_val)/100, int(v_val)/100 )
    elif float(t_val)+float(v_val) -1 < 1e-9:
      # t_val + v_val = 1
      tv_ratio = ( float(t_val), float(v_val) )
    else:
      tv_count_mode = True
      tv_count = (int(t_val), int(v_val))
      tv_ratio = (int(t_val)/(int(t_val)+int(v_val)), int(v_val)/(int(t_val)+int(v_val)))

  with open(anno_file, 'r') as f:
    anno_js = json.load(f)
    new_img_list = {'train':[],
                     'val':[]
                     }
    img_id_tv_map = {}
    new_anno_list = {'train':[],
                     'val':[]
                     }

    # decide train/val
    tv_list = tv_divide(len(anno_js['images']), tv_ratio, tv_count_mode, tv_count)
    # returnd ['train', 'val', 'train', ... ]
    if 'train' in tv_list:
      (img_out_dir / 'train').mkdir(exist_ok=True, parents=True)
    if 'val' in tv_list:
      (img_out_dir / 'val').mkdir(exist_ok=True, parents=True)

    img_finding_prefix = ''
    for i, img in enumerate(anno_js['images']):
      found_img_name = (ps / img_finding_prefix / img['file_name']).resolve()
      while not found_img_name.is_file():
        print("* image not found %s *" % found_img_name)
        print("* please add prefix (ex, train2017/) to image file directory *")
        print("* current_path: %s *" % ps.resolve())
        #pdb.set_trace()
        img_finding_prefix = input("prefix:")
        found_img_name = (ps / img_finding_prefix / img['file_name']).resolve()

      img_name = img['file_name'].split('/')[-1]
      new_img_path = img_out_dir / tv_list[i] / img_name
      print(" copy %s -> %s"%(str(found_img_name), str(new_img_path)))
      shutil.copyfile(found_img_name, str(new_img_path))

      img['file_name'] = tv_list[i] + '/' + img_name
      new_img_list[tv_list[i]].append(img)
      img_id_tv_map[img['id']] = tv_list[i]
    for i, an in enumerate(anno_js['annotations']):
      tv = img_id_tv_map[an['image_id']]
      new_anno_list[tv].append(an)
    new_train_anno_json = {'licenses' : anno_js['licenses'],
                           'info' : anno_js['info'],
                           'categories' : anno_js['categories'],
                           'images' : new_img_list['train'],
                           'annotations' : new_anno_list['train']
                           }
    out_train_anno_file = anno_out_dir / "instances_train.json"
    print('json.dump... %s' % str(out_train_anno_file))
    with open(out_train_anno_file, 'w') as fo:
      json.dump(new_train_anno_json, fo)

    new_valid_anno_json = {'licenses' : anno_js['licenses'],
                           'info' : anno_js['info'],
                           'categories' : anno_js['categories'],
                           'images' : new_img_list['val'],
                           'annotations' : new_anno_list['val']
                           }
    out_valid_anno_file = anno_out_dir / "instances_val.json"
    print('json.dump... %s' % str(out_valid_anno_file))
    with open(out_valid_anno_file, 'w') as fo:
      json.dump(new_valid_anno_json, fo)
    print('copy done')
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

  # TODO : merge lost licenses and info data
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
  img_name_gid_map = {}
  cat_name_gid_map = {}
  anno_g_id = 1
  img_g_id =  1
  cat_g_id = 1
  for anno in annos:
    anno_file = str((ps / anno).resolve())
    print("... read annos %s read "% anno_file)
    imgId_psimg_map_an = {}
    catId_name_map_an = {}
    with open(anno_file, 'r') as f:
      anno_js = json.load(f)
      imgdir_prefix = ''
      for img in anno_js['images']:
        abs_img_path = (ps / imgdir_prefix / img['file_name']).resolve()
        abs_img_name = str(abs_img_path)
        ps_img_name = abs_img_name.split(str(ps.resolve()))[1][1:]
        while not abs_img_path.is_file():
          print("* image not found %s *" % abs_img_name)
          print("* please add prefix (ex, train2017/) to image file directory *")
          print("* current_path: %s *" % ps.resolve())
          #pdb.set_trace()
          imgdir_prefix = input("prefix:")
          abs_img_path = (ps / imgdir_prefix / img['file_name']).resolve()
          abs_img_name = str(abs_img_path)
          ps_img_name = abs_img_name.split(str(ps.resolve()))[1][1:]
        if ps_img_name not in img_name_gid_map.keys():
          img_name_gid_map[ps_img_name] = img_g_id
          all_images.append({'id':img_g_id,
                             'width':img['width'],
                             'height':img['height'],
                             'file_name':ps_img_name,
                             'license':0,
                             'flickr_url':img['flickr_url'],
                             'coco_url':img['coco_url'],
                             'date_captured':img['date_captured']})
          print('img',img, ' -> id:%d'%img_g_id)
          img_g_id += 1
        imgId_psimg_map_an[img['id']] = ps_img_name
      for cat in anno_js['categories']:
        cat_name = cat['name']
        if cat_name not in cat_name_gid_map.keys():
          overwirte_cat = False
          overwrite_name = ''
          for candi_cat in list(cat_name_gid_map.keys()):
            if difflib.SequenceMatcher(a=cat_name, b=candi_cat).ratio() > 0.9:
              print("** there no category %s, but %s is similar **" %(cat_name, candi_cat))
              yn = input("* Do you want to map %s to %s? [y/n]:"%(cat_name, candi_cat))
              overwirte_cat = True if yn == 'y' else False
              if overwirte_cat:
                print("** %d: %s -> %d: %s **" %(cat['id'], cat_name, cat_name_gid_map[candi_cat]+1, candi_cat))
                overwrite_name = candi_cat
                break
          if overwirte_cat:
            cat_name = overwrite_name
          else:
            cat_name_gid_map[cat_name] = cat_g_id
            all_categories.append({'id':cat_g_id,
                                   'name':cat_name,
                                   'supercategory':''})
            print('cat',cat, ' -> id:%d, name:%s'%(cat_g_id, cat_name))
            cat_g_id += 1
        catId_name_map_an[cat['id']] = cat_name
      for ann in anno_js['annotations']:
        new_ann = {'id':anno_g_id,
                   'image_id':img_name_gid_map[imgId_psimg_map_an[ann['image_id']]],
                   'category_id':cat_name_gid_map[catId_name_map_an[ann['category_id']]],
                   'bbox': ann['bbox'],
                   'area': ann['area'],
                   }
        if 'segmentation' in ann.keys():
          new_ann['segmentation'] = ann['segmentation']
        if 'iscrowd' in ann.keys():
          new_ann['iscrowd'] = ann['iscrowd']
        if 'attributes' in ann.keys():
          new_ann['attributes'] = ann['attributes']
        print('ann',ann, ' -> id:%d, image_id:%d, category_id:%d'%(anno_g_id,
                                                             img_name_gid_map[imgId_psimg_map_an[ann['image_id']]],
                                                             cat_name_gid_map[catId_name_map_an[ann['category_id']]])
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

