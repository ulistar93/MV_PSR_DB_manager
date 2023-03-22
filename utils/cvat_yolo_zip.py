#!/usr/bin/env python3
# Author : Changmin Yi
# Create Date : 2023.03.21
# usage example :
#   python cvat_yolo_zip.py --img_dir mdsm+BG+ft2_02_GRAY+ht_GRAY/val/labels --lb_dir mdsm+BG+ft2_02_GRAY+ht_GRAY/val/labels
#                           --save_img --name ~/yolo_val.zip

import argparse
from pathlib import Path
from tqdm import tqdm
import shutil
import zipfile

import pdb

def parse_opt():
  parser = argparse.ArgumentParser()
  parser.add_argument('--img_dir', type=str, default=Path('./images'), help='list image file directory')
  parser.add_argument('--lbs_dir', type=str, default=Path('./labels'), help='labels directory')
  parser.add_argument('--obj_name', type=str, default=Path('./obj_name'), help='class names file')
  parser.add_argument('--save_img', action='store_true', help='default is not include image files')
  parser.add_argument('--name', type=str, default=Path('./yolo.zip'), help='zip file name')
  opt = parser.parse_args()
  return opt

def is_img(img_file):
  suffix = img_file.suffix if isinstance(img_file, Path) else '.' + img_file.split('.')[-1]
  return True if suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"] else False

def cvat_yolo_zip_main(opt):
  lbs_dir = Path(opt.lbs_dir)
  assert lbs_dir.exists(), "lb_dir not found -> abort"
  lbs_list = sorted([x for x in list(lbs_dir.iterdir()) if x.suffix == ".txt"])
  lbs_empty_list = []
  img_dir = Path(opt.img_dir)
  if not img_dir.exists():
    print("img_dir not found; image file names could not be matched with labels name")
    img_list = []
    img_names = [x.stem + ".jpg" for x in lbs_list if is_img(x)]
  else:
    img_list = sorted([x for x in list(img_dir.iterdir()) if is_img(x)])
    img_names = [x.name for x in img_list]
    img_stems = [x.stem for x in img_list]
    lbs_names = [x.name for x in lbs_list]
    for ims in img_stems:
      if not ims + '.txt' in lbs_names:
        lbs_empty_list.append(ims + '.txt')

  obj_name = Path(opt.obj_name)
  assert obj_name.exists(), "obj_name not found -> abort"
  with open(obj_name, 'r') as f_on:
    nc = len([x for x in f_on if x != ""])
  #pdb.set_trace()

  tmp = Path() / ".tmp"
  tmp_data = tmp / "obj_train_data"
  tmp_data.mkdir(parents=True)
  if opt.save_img:
    n_img = len(img_list)
    print("save %d images to .tmp ..." % n_img )
    img_bar = tqdm(img_list, total=n_img, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')
    for im in img_bar:
      shutil.copy(im, tmp_data / im.name )
  for lb in lbs_list:
    shutil.copy(lb, tmp_data / lb.name )
  for lbn in lbs_empty_list:
    with open( tmp_data / lbn , 'w') as f_lbn:
      pass # write nothing
  shutil.copy(obj_name, tmp / obj_name.name )

  with open( tmp / "obj.data", 'w') as f_od:
    f_od.write("classes = %d\n" % nc)
    f_od.write("train = data/train.txt\n")
    f_od.write("names = data/obj.names\n")
    f_od.write("backup = backup/\n")

  with open( tmp / "train.txt", 'w') as f_tt:
    for im in img_names:
      f_tt.write("data/obj_train_data/%s\n" % im)

  zip_name = Path(opt.name)
  if zip_name.suffix == '.zip':
    zip_name = zip_name.parent / zip_name.stem
  shutil.make_archive(zip_name, 'zip', Path(".tmp"))
  #pdb.set_trace()
  print("saved %s.zip" % zip_name)
  shutil.rmtree(".tmp")

if __name__ == "__main__":
  opt = parse_opt()
  cvat_yolo_zip_main(opt)
