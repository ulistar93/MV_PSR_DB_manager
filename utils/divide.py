#!/usr/bin/env python3
# Author : Changmin Yi
# Create Date : 2023.02.02
# usage example :
#   python divide.py --source MDSM_finetune/mdsm+BG --train 0.9 --val 0.1 \
#                    --train_dir MDSM_finetune/mdsm+BG/train_out --val_dir MDSM_finetune/mdsm+BG/val_out

import argparse
from pathlib import Path
import pdb
from tqdm import tqdm
import datetime
import shutil
import math
import random
import numpy as np

def parse_opt(known=False):
  parser = argparse.ArgumentParser()
  parser.add_argument('--source', type=str, required=True, help='images and labels source directory path')
  parser.add_argument('--train', type=float, default=0.9, help='train set ratio')
  parser.add_argument('--val', type=float, default=0.1, help='val set ratio')
  parser.add_argument('--train_dir', type=str, default='', help='output train set directory path')
  parser.add_argument('--val_dir', type=str, default='', help='output val set directory path')
  opt = parser.parse_known_args()[0] if known else parser.parse_args()
  return opt

def divide_main(opt):
  src_dir = Path(opt.source)
  img_src = src_dir / 'images'
  lbs_src = src_dir / 'labels'
  assert img_src.exists(), "images dir not found in %s" % str(src_dir)
  assert lbs_src.exists(), "labels dir not found in %s" % str(src_dir)

  def is_img(img_file):
    suffix = img_file.suffix if isinstance(img_file, Path) else '.' + img_file.split('.')[-1]
    return True if suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp" ] else False
  img_list = sorted([x for x in list(img_src.iterdir()) if is_img(x)])
  n_imgs = len(img_list)
  print("  Found total %d images from img_src," % n_imgs)

  lbs_list = sorted([x for x in list(lbs_src.iterdir()) if x.suffix == ".txt"])
  n_labels = len(lbs_list)
  print("  Found %d filtered labels," % n_labels)
  lbs_names = [x.stem for x in lbs_list]

  stem_id = {}
  img_lb_tv_list = []
  for i, im in enumerate(img_list):
    stem_id[im.stem] = i
    img_lb_tv_list.append([im, '', 0])
  for lb in lbs_list:
    idx = stem_id[lb.stem]
    img_lb_tv_list[idx][1] = lb
  img_lb_tv_list = np.array(img_lb_tv_list)

  assert math.isclose(opt.train + opt.val, 1), "opt train + val should be 1"
  nt = round(n_imgs * opt.train)
  nv = round(n_imgs * opt.val)
  nv += n_imgs - nt - nv
  tv_list = [0]*nt + [1]*nv
  random.shuffle(tv_list)

  while True:
    img_lb_tv_list[:,2] = tv_list
    im_t, im_v, lb_t, lb_v = 0, 0, 0, 0
    for im,lb,tv in img_lb_tv_list:
      if tv == 0: # train
        im_t +=1
        if lb:
          lb_t +=1
      elif tv == 1: # train
        im_v +=1
        if lb:
          lb_v +=1
    print("            train /    val")
    print("  images : %6d / %6d" % (im_t, im_v))
    print("  labels : %6d / %6d" % (lb_t, lb_v))
    #pdb.set_trace()
    redo = input(" * re-shuffle? [r]edo [c]ontinue [q]uit : ")
    if redo == 'q':
      exit()
    elif redo == 'c':
      break
    elif redo == 'r':
      random.shuffle(tv_list)
      continue
    else:
      print(" * no shuffle and re-input *")
      continue

  pdb.set_trace()
  print("* copy images & labels ... *")
  train_dir = Path(opt.train_dir) if opt.train_dir else src_dir / "train"
  train_images = train_dir / "images"
  train_labels = train_dir / "labels"
  val_dir = Path(opt.val_dir) if opt.val_dir else src_dir / "val"
  val_images = val_dir / "images"
  val_labels = val_dir / "labels"
  try:
    train_dir.mkdir(exist_ok=False)
    train_images.mkdir(exist_ok=False)
    train_labels.mkdir(exist_ok=False)
  except:
    print("  * --train_dir already exist, overwriting is forbidden * -> abort")
    exit()
  try:
    val_dir.mkdir(exist_ok=False)
    val_images.mkdir(exist_ok=False)
    val_labels.mkdir(exist_ok=False)
  except:
    print("  * --val_dir already exist, overwriting is forbidden * -> abort")
    exit()

  train_list = []
  val_list = []
  for img, lb, tv in img_lb_tv_list:
    if tv == 0: #train
      train_list.append([img, lb])
    else: #train
      val_list.append([img, lb])

  assert len(train_list) == nt, " make train list failed"
  assert len(val_list) == nv, " make val list failed"
  print("* copy train *")
  train_list = tqdm(train_list, total=nt, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')
  for im, lb in train_list:
    img_dst = train_images / im.name
    shutil.copy2(im, img_dst)
    if lb:
      lb_dst = train_labels / lb.name
      shutil.copy2(lb, lb_dst)
  print("* copy val *")
  val_list = tqdm(val_list, total=nv, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')
  for im, lb in val_list:
    img_dst = val_images / im.name
    shutil.copy2(im, img_dst)
    if lb:
      lb_dst = val_labels / lb.name
      shutil.copy2(lb, lb_dst)
  print("* done *")

if __name__ == "__main__":
  opt = parse_opt()
  divide_main(opt)
