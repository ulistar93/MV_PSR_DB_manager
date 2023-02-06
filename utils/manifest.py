#!/usr/bin/env python3
# Author : Changmin Yi
# Create Date : 2023.01.04
# usage example :
#   python manifest.py --labels PSR_VALSET_v0/val/labels

import argparse
from pathlib import Path
import pdb
from tqdm import tqdm

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
  parser.add_argument('--save_dir', type=str, default='', help='save labels.jpg location')
  parser.add_argument('--no_save_txt', action='store_true', help='no save labes_stat.txt')
  opt = parser.parse_known_args()[0] if known else parser.parse_args()
  return opt

class Colors:
    # Ultralytics color palette https://ultralytics.com/
    def __init__(self):
        # hex = matplotlib.colors.TABLEAU_COLORS.values()
        hex = ('FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
               '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')
        self.palette = [self.hex2rgb('#' + c) for c in hex]
        self.n = len(self.palette)

    def __call__(self, i, bgr=False):
        c = self.palette[int(i) % self.n]
        return (c[2], c[1], c[0]) if bgr else c

    @staticmethod
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))

colors = Colors()  # create instance for 'from utils.plots import colors'

def xyxy2xywh(x):
    # Convert nx4 boxes from [x1, y1, x2, y2] to [x, y, w, h] where xy1=top-left, xy2=bottom-right
    y = np.copy(x)
    y[:, 0] = (x[:, 0] + x[:, 2]) / 2  # x center
    y[:, 1] = (x[:, 1] + x[:, 3]) / 2  # y center
    y[:, 2] = x[:, 2] - x[:, 0]  # width
    y[:, 3] = x[:, 3] - x[:, 1]  # height
    return y

def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    #y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y

# lables :
# array([[          5,        0.29,     0.62898,        0.09,     0.17797],
#       [          2,     0.23669,     0.60934,     0.20912,     0.16914]], dtype=float32)
# names : ['Cigarette', 'E_Cigarette', 'Hand', 'Bottle', 'Cup', 'Cell_Phone']
def plot_labels(labels, names=(), save_dir=Path(''), save_txt=''):
    txt_str = ""
    # plot dataset labels
    print("Plotting labels to %s/labels.jpg ... " % (save_dir))
    c, b = labels[:, 0], labels[:, 1:].transpose()  # classes, boxes
    nc = int(c.max() + 1)  # number of classes
    x = pd.DataFrame(b.transpose(), columns=['x', 'y', 'width', 'height'])

    # seaborn correlogram
    sn.pairplot(x, corner=True, diag_kind='auto', kind='hist', diag_kws=dict(bins=50), plot_kws=dict(pmax=0.9))
    plt.savefig(save_dir / 'labels_correlogram.jpg', dpi=200)
    plt.close()

    # matplotlib labels
    matplotlib.use('svg')  # faster
    ax = plt.subplots(2, 2, figsize=(8, 8), tight_layout=True)[1].ravel()
    # ax[0]
    y = ax[0].hist(c, bins=np.linspace(0, nc, nc + 1) - 0.5, rwidth=0.8)
    try:  # color histogram bars by class
        [y[2].patches[i].set_color([x / 255 for x in colors(i)]) for i in range(nc)]  # known issue #3195
    except Exception:
        pass
    ax[0].set_ylabel('instances')
    txt_str += "instances: total %d\n" % np.sum(y[0][:])

    if 0 < len(names) < 30:
        ax[0].set_xticks(range(len(names)))
        ax[0].set_xticklabels(names, rotation=90, fontsize=10)
    else:
        ax[0].set_xlabel('classes')
    for ic in range(nc):
        ax[0].text(ic - 0.4, y[0][ic] + 10, int(y[0][ic]), size=10)
        txt_str += "\t%s = %d\n" % (names[ic], int(y[0][ic]))
    # ax[2]
    sn.histplot(x, x='x', y='y', ax=ax[2], bins=50, pmax=0.9)
    # ax[3]
    sn.histplot(x, x='width', y='height', ax=ax[3], bins=50, pmax=0.9)

    # ax[1]
    # rectangles
    labels[:, 1:3] = 0.5  # center
    labels[:, 1:] = xywh2xyxy(labels[:, 1:]) * 2000
    img = Image.fromarray(np.ones((2000, 2000, 3), dtype=np.uint8) * 255)
    for cls, *box in labels[:1000]:
        ImageDraw.Draw(img).rectangle(box, width=1, outline=colors(cls))  # plot
    ax[1].imshow(img)
    ax[1].axis('off')

    for a in [0, 1, 2, 3]:
        for s in ['top', 'right', 'left', 'bottom']:
            ax[a].spines[s].set_visible(False)
    plt.savefig(save_dir / 'labels.jpg', dpi=200)

    if save_txt:
        with open(save_dir / save_txt, 'w') as f:
            f.write(txt_str)

    matplotlib.use('Agg')
    plt.close()
    print("Plotting labels done")

def plot_labels2(labels, names=(), save_dir=Path(''), save_txt=''):
    txt_str = ""
    # plot dataset labels
    print("Plotting labels to %s/labels2.jpg ... " % (save_dir))
    img_dir = save_dir / 'images'
    if img_dir.exists():
        print("images dir found %s" % (img_dir))
    imids = list(map(int, labels[:, 0])) # image ids
    lbids = list(map(int, labels[:, 1])) # label ids
    c, b = labels[:, 2], labels[:, 3:].transpose()  # classes, boxes
    nc = int(c.max() + 1)  # number of classes
    labeled_img_count = max(imids) + 1
    def is_img(img_file):
        suffix = img_file.suffix if isinstance(img_file, Path) else '.' + img_file.split('.')[-1]
        return True if suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp"] else False
    all_img_count = len([x for x in list(img_dir.iterdir()) if is_img(x)]) if img_dir.exists() else 0
    txt_str += "images: %d labeled / " % labeled_img_count
    txt_str += "%d images\n" % all_img_count if all_img_count != 0 else "? images\n"

    cat_img_set = {}
    img_lb_rank = []
    #img_cat_rank = {}
    for i, l, cc in zip(imids, lbids, c):
        if i < len(img_lb_rank):
            img_lb_rank[i] = max(img_lb_rank[i], l+1)
        else:
            img_lb_rank.append(1)
        if cc in cat_img_set.keys():
            cat_img_set[cc].add(i)
        else:
            cat_img_set[cc] = set([i])
    cat_img_count = [ len(cat_img_set[x]) for x in range(nc) ]

    # matplotlib labels
    matplotlib.use('svg')  # faster
    ax = plt.subplots(1, 2, figsize=(8, 4), tight_layout=True)[1].ravel()
    # ax[0]
    y = ax[0].bar(list(range(nc)),cat_img_count, width=0.8)
    ax[0].set_ylabel('images')

    if 0 < len(names) < 30:
        ax[0].set_xticks(range(len(names)))
        ax[0].set_xticklabels(names, rotation=90, fontsize=10)
    else:
        ax[0].set_xlabel('classes')
    for ic in range(nc):
        ax[0].text(ic - 0.4, cat_img_count[ic] + 10, int(cat_img_count[ic]), size=10)
        txt_str += "\t%s = %d\n" % (names[ic], int(cat_img_count[ic]))

    txt_str += "rank (#labels/image): \n"
    max_lb = max(img_lb_rank)
    if all_img_count > labeled_img_count:
        img_lb_rank += [0] * (all_img_count - labeled_img_count)
    y2 = ax[1].hist(img_lb_rank, bins=np.linspace(0, max_lb, max_lb + 1) - 0.5, rwidth=0.8)
    ax[1].set_ylabel('images')
    ax[1].set_xlabel('rank (#lb/#img)')
    ax[1].set_xticks(range(max_lb))
    for ic in range(max_lb):
        ax[1].text(ic - 0.4, y2[0][ic] + 10, int(y2[0][ic]), size=10)
        txt_str += "\trank %d = %d\n" % (ic, int(y2[0][ic]))

    for a in [0, 1]:
        for s in ['top', 'right']:
            ax[a].spines[s].set_visible(False)
    plt.savefig(save_dir / 'labels2.jpg', dpi=200)

    if save_txt:
        with open(save_dir / save_txt, 'w') as f:
            f.write(txt_str)

    matplotlib.use('Agg')
    plt.close()
    print("Plotting labels2 done")

def manifest_main(opt):
  lbs_dir = Path(opt.labels)
  lbs_txt = [x for x in list(lbs_dir.iterdir()) if x.suffix == ".txt"]
  n_labels = len(lbs_txt)
  print("Found %d label files and read ..." % (n_labels))
  lbs_txt = sorted(lbs_txt)
  if n_labels > 1000:
    lbs_txt = tqdm(lbs_txt, total=n_labels, bar_format='{l_bar}{bar:20}{r_bar}{bar:-20b}')
  labels = []
  for imid, lbs_file in enumerate(lbs_txt):
    lb = []
    with open(lbs_file, 'r') as f:
      for lid, line in enumerate(f):
        line = line.strip().split(' ')
        line = [imid, lid] + line
        lb.append(line)
    labels.append(np.array(lb, dtype=np.float32))
  labels = np.concatenate(labels, 0)

  names = []
  names_file = lbs_dir / "obj.names" if (lbs_dir / "obj.names").exists() else lbs_dir.parent / "obj.names"
  if names_file.exists():
    with open(names_file, 'r') as f:
      for line in f:
        names.append(line.strip())
  else:
    print(" * obj.names file not found -> category name will be shown as 0,1,2,... numbers *")
  save_dir = opt.save_dir if opt.save_dir else lbs_dir.parent
  save_txt = '' if opt.no_save_txt else "labels_stat.txt"

  plot_labels(labels[:,2:], names, save_dir, save_txt)
  plot_labels2(labels, names, save_dir, save_txt)

#def run(**kwargs):
#  # Usage: import manifest; manifest.run(source='Datasets/mdsm_capture_psr', imgsz=320, weights='yolov5m.pt')
#  opt = parse_opt(True)
#  for k, v in kwargs.items():
#    setattr(opt, k, v)
#  manifest_main(opt)
#  return opt

if __name__ == "__main__":
  opt = parse_opt()
  manifest_main(opt)
