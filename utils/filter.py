#!/usr/bin/env python3
# Author : Changmin Yi
# Create Date : 2023.01.05
# usage example :
#   python filter.py --labels PSR_VALSET_v0/val/labels --include 0 2 5
#   python filter.py --labels PSR_VALSET_v0/val/labels --exclude 1 3 4
#   python filter.py --labels PSR_VALSET_v0/val/labels --include 0 2 5 \
#                    --copy_img --img_src PSR_VALSET_v0/val/images --img_dst PSR_VALSET_v0/val/images_filtered
#   python filter.py --labels train_dev/labels --include 0 2 5 --copy_img --img_src train_dev/images/ --img_dst /home/algo/_smoking+ddd+pexels+unsplash+aihub/train_dev/images_filtered
#   python filter.py --labels train/labels --include 0 2 5 --copy_img --img_src train/images/ --img_dst /home/algo/_smoking+ddd+pexels+unsplash+aihub/train/images_filtered

import argparse
from pathlib import Path
import pdb
from tqdm import tqdm
import datetime
import shutil

import cv2
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sn
from PIL import Image, ImageDraw, ImageFont

def parse_opt(known=False):
  parser = argparse.ArgumentParser()
  parser.add_argument('--labels', type=str, required=True, help='yolo type labels directory path')
  parser.add_argument('--include', nargs='+', type=int, help='the labels index want to keep')
  parser.add_argument('--exclude', nargs='+', type=int, help='the labels index want to remove')
  parser.add_argument('--save_dir', type=str, default='', help='save filtered labels location')
  parser.add_argument('--copy_img', action='store_true', help='copy image files from img_src to img_dst')
  parser.add_argument('--img_src', type=str, default='', help='image source directory for copying')
  parser.add_argument('--img_dst', type=str, default='', help='image destination directory for copying')
  opt = parser.parse_known_args()[0] if known else parser.parse_args()
  return opt

def filter_labels(opt_labels, category_map, save_dir=Path(''), include_mode=True):
  if not save_dir.exists():
    save_dir.mkdir(parents=True, exist_ok=True)

  lbs_dir = Path(opt.labels)
  lbs_txt = [x for x in list(lbs_dir.iterdir()) if x.suffix == ".txt"]
  n_labels = len(lbs_txt)
  lbs_txt = sorted(lbs_txt)
  print("Found %d label files and read ..." % (n_labels))
  if n_labels > 1000:
    lbs_txt = tqdm(lbs_txt, total=n_labels, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')
  cmap_changed = False
  for lbs_file in lbs_txt:
    out_file = save_dir / lbs_file.name
    #print("%s -> %s" % (lbs_file, out_file))
    out_txt = ''
    with open(lbs_file, 'r') as fr:
      for line in fr:
        c, *box = line.strip().split(' ')
        c = int(c)
        if c not in category_map.keys():
          category_map[c] = -1 if include_mode else max(category_map.values()) + 1
          cmap_changed = True
        new_c = category_map[c]
        if new_c == -1:
          continue
        else:
          #fw.write(" ".join([str(new_c)] + box) + '\n')
          out_txt += " ".join([str(new_c)] + box) + '\n'
    if out_txt:
      open(out_file, 'w').write(out_txt)
      #with open(out_file, 'w') as fw:
      #  fw.write(out_txt)
  print("* label filtering done *")
  if cmap_changed:
    return category_map
  return {}

def print_category_map(cmap, names, fin=False):
  cmap_str = ''
  for k in sorted(cmap.keys()):
    cmap_str += str(k)
    cmap_str += ": %-11s -> " % names[k] if names else ": '' -> "
    cmap_str += str(cmap[k]) if cmap[k] != -1 else ''
    cmap_str += '\n'
  if not names and not fin:
    cmap_str += '... (undefined end; obj.names not found)\n'
  print(cmap_str.strip())

def save_new_obj_name(cmap, names, save_dir):
  if names:
    new_obj_file = save_dir.parent / "obj_filtered.names"
    with open(new_obj_file, 'w') as f:
      for k, v in cmap.items():
        if v != -1:
          f.write(names[k].strip() + '\n')
  else:
    print("* failed to write obj_filtered.names : not found obj.names *")

  save_cmap_file = save_dir.parent / "filter_map.txt"
  filtered_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
  with open(save_cmap_file, 'w') as f:
    f.write("Filtered date : %s\n" % filtered_date)
    cmap_str = ''
    for k in sorted(cmap.keys()):
      cmap_str += str(k)
      cmap_str += ": %-11s -> " % names[k] if names else ": '' -> "
      cmap_str += str(cmap[k]) if cmap[k] != -1 else ''
      cmap_str += '\n'
    f.write(cmap_str)
  print("* save new obj.names file done *")

def copy_img_files(opt, filtered_labels_saved_dir):
  print("* copy filtered images ... *")
  img_src = Path(opt.img_src)
  if not img_src:
    print("  * --img_src required for --copy_img * -> abort")
    exit()
  print("                   from %s" % str(img_src))
  img_dst = Path(opt.img_dst) if opt.img_dst else img_src.parent / "images_filtered"
  try:
    img_dst.mkdir(parents=True, exist_ok=False)
  except:
    print("  * --img_dst already exist, overwriting is forbidden * -> abort")
    exit()
  print("                     to %s" % str(img_dst))

  def is_img(img_file):
    suffix = img_file.suffix if isinstance(img_file, Path) else '.' + img_file.split('.')[-1]
    return True if suffix in [".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".bmp", ".BMP"] else False
  img_list = sorted([x for x in list(img_src.iterdir()) if is_img(x)])
  total_imgs = len(img_list)
  print("  Found total %d images from img_src," % total_imgs)

  lbs_txt = sorted([x for x in list(filtered_labels_saved_dir.iterdir()) if x.suffix == ".txt"])
  lbs_names = [x.stem for x in lbs_txt]
  n_labels = len(lbs_txt)
  print("  Found %d filtered labels," % n_labels)

  img_name_suffix_map = {}
  for img_file in img_list:
    img_name_suffix_map[img_file.stem] = img_file.suffix
  img_names = list(img_name_suffix_map.keys())
  matched_names = [x for x in lbs_names if x in img_names]
  n_imgs = len(matched_names)
  print("  Found %d matched images (to be copied) ..." % n_imgs)


  if n_imgs > 1000:
    matched_names = tqdm(matched_names, total=n_imgs, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')
  for file_stem in matched_names:
    file_suffix = img_name_suffix_map[file_stem]
    file_name = file_stem + file_suffix
    img_src_file = img_src / file_name
    img_dst_file = img_dst / file_name
    if not img_src_file.exists():
      print("* image '%s' not found *" % img_src_file)
      continue
    shutil.copy2(img_src_file, img_dst_file)
    #shutil.copy(img_src_file, img_dst_file)
  print("* copy images done *" % ())

def filter_main(opt):
  lbs_dir = Path(opt.labels)
  nc, names = 0, []
  names_file = lbs_dir / "obj.names" if (lbs_dir / "obj.names").exists() else lbs_dir.parent / "obj.names"
  if names_file.exists():
    with open(names_file, 'r') as f:
      for line in f:
        names.append(line.strip())
    nc = len(names)
  else:
    print("obj.names file not found -> category name will be shown as 0,1,2,... numbers")

  save_dir = Path(opt.save_dir) if opt.save_dir else lbs_dir.parent / "labels_filtered"

  cmap = {}
  if opt.include:
    if opt.exclude:
      print("include and exclude both given -> include only works")
    t_nc = nc if nc != 0 else max(opt.include) + 1
    t_c = 0
    for i in range(t_nc):
      if i in opt.include:
        cmap[i] = t_c
        t_c += 1
      else:
        cmap[i] = -1
    print("* category change *")
    print_category_map(cmap, names, fin=False)

    changed_cmap = filter_labels(opt.labels, cmap, save_dir, include_mode=True)
  elif opt.exclude:
    t_nc = nc if nc != 0 else max(opt.exclude) + 1
    t_c = 0
    for i in range(t_nc):
      if i in opt.exclude:
        cmap[i] = -1
      else:
        cmap[i] = t_c
        t_c += 1
    print("* category change *")
    print_category_map(cmap, names, fin=False)

    changed_cmap = filter_labels(opt.labels, cmap, save_dir, include_mode=False)
  else:
    print("* at least one option require among include and exclude *")
    exit()

  if changed_cmap:
    print_category_map(changed_cmap, names, fin=True)
    save_new_obj_name(changed_cmap, names, save_dir)
  else:
    save_new_obj_name(cmap, names, save_dir)

  if opt.copy_img:
    copy_img_files(opt, save_dir)
#def run(**kwargs):
#  # Usage: import manifest; manifest.run(source='Datasets/mdsm_capture_psr', imgsz=320, weights='yolov5m.pt')
#  opt = parse_opt(True)
#  for k, v in kwargs.items():
#    setattr(opt, k, v)
#  manifest_main(opt)
#  return opt

if __name__ == "__main__":
  opt = parse_opt()
  filter_main(opt)
