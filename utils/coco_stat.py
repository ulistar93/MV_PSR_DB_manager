# coco_stat.py
#   read coco annotation json and show statistic
#
# usage:
#   python coco_stat.py [annotaiton file]
#
# date:
#   2022.04.15 Changmin Yi

import sys, os
from pycocotools.coco import COCO
import pdb

if len(sys.argv) < 2:
  print("py require anno_file name")
  print("ex) python coco_stat.py instances_default.json")
  exit(0)

anno_file = sys.argv[1]
print('load coco... %s' % anno_file)
coco = COCO(anno_file)

catIds = coco.getCatIds()
img_cnt = {}
anno_cnt = {}
for cid in catIds:
  img_cnt[cid] = len(coco.getImgIds(catIds=cid))
  anno_cnt[cid] = len(coco.getAnnIds(catIds=cid))

# print anno stat
print("\n** print anno stat **")
for cid in catIds:
  cname = coco.loadCats(cid)[0]['name']
  print("  %d:%s = %d" % (cid, cname, anno_cnt[cid]))
print("all annos = %d" % len(coco.getAnnIds()))

# print img stat
print("\n** print img stat **")
for cid in catIds:
  cname = coco.loadCats(cid)[0]['name']
  print("  %d:%s = %d" % (cid, cname, img_cnt[cid]))
print("all imgs = %d" % len(coco.getImgIds()))

train_img_cnt = 0
val_img_cnt = 0
for im_k in coco.imgs.keys():
  fname = coco.imgs[im_k]['file_name']
  if '/' in fname:
    train_img_cnt += 1 if 'train' in fname.split('/')[0] else 0
    val_img_cnt += 1 if 'val' in fname.split('/')[0] else 0

if train_img_cnt != 0 or val_img_cnt != 0:
  print("\n** print img train/val ratio **")
  print("  %d:%d = %.2f:%.2f" % (train_img_cnt, val_img_cnt,
                                 train_img_cnt/(train_img_cnt+val_img_cnt),
                                 val_img_cnt/(train_img_cnt+val_img_cnt)))
