#!/usr/bin/env python3
# Author : Changmin Yi
# Create Date : 2023.01.09
# usage example :
#   python crop_roi.py --lb_src PSR_VALSET_v0/val/labels_filtered --lb_dst PSR_VALSET_v0/val/labels_f_cropped \
#                      --img_src PSR_VALSET_v0/val/images_filtered --img_dst PSR_VALSET_v0/val/images_f_cropped \
#                      --keep_ciga --crop_tag _handcropped \
#                      --roi_base 1 --roi_margin 0.5 0.5 0.5 0
#
#   python crop_roi.py --lb_src train_dev/labels_f --lb_dst train_dev/labels_fc \
#                      --img_src train_dev/images_f --img_dst train_dev/images_fc \


import argparse
from pathlib import Path
import pdb
from tqdm import tqdm
import datetime
import shutil
import math

import cv2
#import matplotlib
#import matplotlib.pyplot as plt
import numpy as np
#import pandas as pd
#import seaborn as sn
#from PIL import Image, ImageDraw, ImageFont

def parse_opt(known=False):
  parser = argparse.ArgumentParser()
  parser.add_argument('--lb_src', type=str, required=True, help='original labels directory (yolo type)')
  parser.add_argument('--lb_dst', type=str, help='cropped & re-arranged labels directory')
  parser.add_argument('--img_src', type=str, required=True, help='original images directory')
  parser.add_argument('--img_dst', type=str, help='cropped images directory')
  parser.add_argument('--roi_base', type=int, default=1, help='the base category for roi')
  parser.add_argument('--roi_margin', nargs='+', type=float, default=[.5, .5, .5, .0], help='ratio margin for roi * max(dw,dh)')
  parser.add_argument('--crop_tag', type=str, help='cropped image name tag. recommand start with _')
  parser.add_argument('--keep_ciga', action='store_true', help='keep ciga label even if out of Hand roi')

  #parser.add_argument('--exclude', nargs='+', type=int, help='the labels index want to remove')
  #parser.add_argument('--save_dir', type=str, default='', help='save filtered labels location')
  #parser.add_argument('--copy_img', action='store_true', help='copy image files from img_src to img_dst')
  opt = parser.parse_known_args()[0] if known else parser.parse_args()
  return opt

def xywhn2xyxy(x, w, h):
  sx = w * (x[0] - x[2] / 2)
  sy = h * (x[1] - x[3] / 2)
  ex = w * (x[0] + x[2] / 2)
  ey = h * (x[1] + x[3] / 2)
  return [sx, sy, ex, ey]

def xyxy2xywhn(x, w, h):
  cx = ((x[0] + x[2]) / 2) / w
  cy = ((x[1] + x[3]) / 2) / h
  dw = (x[2] - x[0]) / w
  dh = (x[3] - x[1]) / h
  return [cx, cy, dw, dh]

def box_center_in(boxA, boxB):
  # if boxA is inside of boxB -> True
  # box = [sx, sy, ex, ey]
  cx = (boxA[0] + boxA[2]) / 2
  cy = (boxA[1] + boxA[3]) / 2
  return boxB[0] <= cx <= boxB[2] and boxB[1] <= cy <= boxB[3]

def roi_crop(org_img, roi_xyxy, bboxes):
  rsx, rsy, rex, rey = roi_xyxy
  cropped_img = org_img[rsy:rey,rsx:rex]
  cropped_boxes = []
  for bb in bboxes:
    cbb_cat = bb[0]
    cbb_sx = max(0, bb[1] - rsx)
    cbb_sy = max(0, bb[2] - rsy)
    cbb_ex = min(bb[3] - rsx, rex - rsx)
    cbb_ey = min(bb[4] - rsy, rey - rsy)
    cbb_box = [cbb_sx, cbb_sy, cbb_ex, cbb_ey]
    cropped_boxes.append([cbb_cat] + cbb_box)
  return cropped_img, cropped_boxes

def crop_img_yolo(img_file, img_dst_dir, lb_file, lb_dst_dir,
             base=1, roi=[.5,.5,.5,0], crop_tag='', keep_ciga=False):
  img = cv2.imread(str(img_file))
  h, w, c = img.shape
  _stem = img_file.stem
  _tag = crop_tag if crop_tag else "_%dcropeed" % roi_base
  _suffix = img_file.suffix

  # *_bboxes = [[cat_id, sx, sy, ex, ey ], ... ]
  #              cat_id : int
  #              sy, sy, ex, ey : float cordinate
  all_bboxes = []
  with open(lb_file, 'r') as fr:
    for line in fr:
      bb = line.strip().split(' ')
      bb_cat = int(bb[0])
      bb_box_xywhn = list(map(float, bb[1:]))
      bb_box_xyxy = xywhn2xyxy(bb_box_xywhn, w, h)
      all_bboxes.append([bb_cat] + bb_box_xyxy)
  base_bboxes = []
  other_bboxes = []
  for bb in all_bboxes:
    if bb[0] == base:
      base_bboxes.append(bb)
    else:
      other_bboxes.append(bb)

  roi_list = []
  roi_bboxes = []
  for bb in base_bboxes:
    sx, sy, ex, ey = bb[1:]
    dm = max(ex - sx, ey - sy)
    rsx = max(0, math.floor(sx - dm * roi[0])) # left
    rsy = max(0, math.floor(sy - dm * roi[2])) # up
    rex = min(w, math.ceil(ex + dm * roi[1])) # right
    rey = min(h, math.ceil(ey + dm * roi[3])) # bottom
    roi_list.append([rsx, rsy, rex, rey])
    roi_bboxes.append([])
  for bb in all_bboxes:
    for i, r in enumerate(roi_list):
      if box_center_in(bb[1:], r):
        roi_bboxes[i].append(bb)

  if keep_ciga:
    for bb in other_bboxes:
      if bb[0] == 0: # ciga
        # check ciga is in rois
        ciga_included = False
        for i, r in enumerate(roi_list):
          if box_center_in(bb[1:], r):
            ciga_included = True
            break
        if ciga_included:
          continue
        else:
          sx, sy, ex, ey = bb[1:]
          dm = max(ex - sx, ey - sy)
          rsx = max(0, math.floor(sx - dm * roi[0])) # left
          rsy = max(0, math.floor(sy - dm * roi[2])) # up
          rex = min(w, math.ceil(ex + dm * roi[1])) # right
          rey = min(h, math.ceil(ey + dm * roi[3])) # bottom
          ciga_roi = [rsx, rsy, rex, rey]
          ciga_roi_bboxes = []
          for bb in all_bboxes:
            if box_center_in(bb[1:], ciga_roi):
              ciga_roi_bboxes.append(bb)
          roi_list.append(ciga_roi)
          roi_bboxes.append(ciga_roi_bboxes)

  # write roi
  for i, (r, bs) in enumerate(zip(roi_list, roi_bboxes)):
    cropped_img, cropped_boxes = roi_crop(img, r, bs)
    rh, rw, _ = cropped_img.shape
    out_img_file = img_dst_dir / (_stem + _tag + str(i) + _suffix)
    out_lb_file = lb_dst_dir / (_stem + _tag + str(i) + '.txt')
    cv2.imwrite(str(out_img_file), cropped_img)
    # TODO - no bbox still make a txt file too -> To be check
    with open(out_lb_file, 'w') as fw:
      for bb in cropped_boxes:
        bb_cat = int(bb[0])
        bb_box_xyxy = bb[1:]
        bb_box_xywhn = xyxy2xywhn(bb_box_xyxy, rw, rh)
        bb_box_str = ' '.join(list(map(str, [bb_cat] + bb_box_xywhn))) + '\n'
        fw.write(bb_box_str)

def crop_main(opt):
  roi_base = opt.roi_base
  print("* crop images by category %d *" % roi_base)

  lb_src = Path(opt.lb_src)
  lb_dst = Path(opt.lb_dst) if opt.lb_dst else lb_src.parent / (lb_src.name + "_%dcropped" % roi_base)

  if not lb_dst.exists():
    lb_dst.mkdir(parents=True, exist_ok=True)
  assert (lb_src.exists() and lb_dst.exists())
  print(" labels copy %s -> %s" %(str(lb_src), str(lb_dst)))

  img_src = Path(opt.img_src)
  img_dst = Path(opt.img_dst) if opt.img_dst else img_src.parent / (img_src.name + "_%dcropped" % roi_base)
  if not img_dst.exists():
    img_dst.mkdir(parents=True, exist_ok=True)
  assert (img_src.exists() and img_dst.exists())
  print(" images copy %s -> %s" %(str(img_src), str(img_dst)))

  crop_logf = open(img_dst.parent / "crop_log.txt", 'w')
  cropped_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
  crop_logf.write("Cropped date : %s\n" % cropped_date)
  crop_logf.write("* crop images by category %d *\n" % roi_base)
  crop_logf.write(" labels copy %s -> %s\n" %(str(lb_src), str(lb_dst)))
  crop_logf.write(" images copy %s -> %s\n" %(str(img_src), str(img_dst)))

  def is_img(img_file):
    suffix = img_file.suffix if isinstance(img_file, Path) else '.' + img_file.split('.')[-1]
    return True if suffix in [".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".bmp", ".BMP"] else False
  img_list = sorted([x for x in list(img_src.iterdir()) if is_img(x)])
  n_imgs = len(img_list)
  print(" Found total %d images from img_src ..." % n_imgs)
  crop_logf.write(" Found total %d images from img_src ..." % n_imgs)
  if n_imgs > 1000:
    img_list = tqdm(img_list, total=n_imgs, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')
  for img_file in img_list:
    lb_file = lb_src / (img_file.stem + '.txt')
    if lb_file.exists():
      crop_img_yolo(img_file, img_dst,
                    lb_file, lb_dst,
                    base=roi_base, roi=opt.roi_margin[:4],
                    crop_tag=opt.crop_tag, keep_ciga=opt.keep_ciga)
  print("* crop img done *")
  crop_logf.write("* crop img done *\n")
  crop_logf.close()

#def run(**kwargs):
#  # Usage: import manifest; manifest.run(source='Datasets/mdsm_capture_psr', imgsz=320, weights='yolov5m.pt')
#  opt = parse_opt(True)
#  for k, v in kwargs.items():
#    setattr(opt, k, v)
#  manifest_main(opt)
#  return opt

if __name__ == "__main__":
  opt = parse_opt()
  crop_main(opt)
