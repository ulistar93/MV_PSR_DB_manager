#!/home/ycm/torch1.8/bin/python
# Author : Changmin Yi
# Date : 2023.01.03

# usage example
# ./bbox_viewer2.py --dataset PSR_VALSET_v0/val/ --roi --window 500 150
# ./bbox_viewer2.py --dataset datasets/smoking+ddd+pexels+unsplash+aihub/train_dev --roi --window 500 25 --imgsz 720 480

from pathlib import Path
ROOT = Path()

import argparse
import pdb

import cv2
import numpy as np

def set_box_fn(opt, h, w):
  def COCO2bbox(bx):
    sx, sy, ex, ey = bx # TODO
    return (sx, sy), (ex, ey)
  def YOLO2bbox(bx):
    cx, dw = bx[0]*w, bx[2]*w
    cy, dh = bx[1]*h, bx[3]*h
    sx, ex = int(cx - dw/2), int(cx + dw/2)
    sy, ey = int(cy - dh/2), int(cy + dh/2)
    return (sx, sy), (ex, ey)
  if opt.coco:
    return COCO2bbox
  else:
    return YOLO2bbox

color_pal = [
  [0,0,255],    # red
  [238,130,238], # pink
  [0,124,255],  # orange
  [0,255,255],  # yellow
  [0,192,128],  # green
  [255,255,0],  # cyan
  #[255,0,0],    # blue
]

def draw_bbox(opt, im, bboxes):
  h, w, c = im.shape
  box_fn = set_box_fn(opt,h,w)
  for bb in bboxes:
    col = color_pal[bb[0]]
    p1, p2 = box_fn(bb[1:])
    cv2.rectangle(im, p1, p2, col, 2)
    if opt.roi and int(opt.roi_margin[0]) == bb[0]:
      dw, dh = p2[0] - p1[0], p2[1] - p1[1] # ver1. 각각 dw,dh 비례
      d = max(dw, dh)
      dw, dh = d, d
      rp1 = (int(p1[0] - dw * opt.roi_margin[1]),# left
             int(p1[1] - dh * opt.roi_margin[3])) # up
      rp2 = (int(p2[0] + dw * opt.roi_margin[2]), # right
             int(p2[1] + dh * opt.roi_margin[4])) # down
      cv2.rectangle(im, rp1, rp2, np.array(col) + np.ones((3,)) * 100 , 1)
  return

def main(opt):
  if opt.dataset:
    imdir = Path(opt.dataset) / "images"
    lbdir = Path(opt.dataset) / "labels"
  else:
    imdir = Path(opt.images)
    lbdir = Path(opt.labels)
  assert (imdir.exists()),"images dir not exist"
  def isimg(x):
    return True if x.suffix in ['.jpg', '.jpeg', '.png', '.JPG', '.PNG'] else False
  imdir_list = sorted([ x for x in list(imdir.iterdir()) if isimg(x) ])
  lbdir_list = sorted([ x for x in list(lbdir.iterdir()) if x.suffix == '.txt'])
  #imdir_list = sorted(list(imdir.iterdir()))
  #lbdir_list = sorted(list(lbdir.iterdir()))
  i, max_i = 0, len(imdir_list) - 1
  END = False

  print("  keys:")
  print("    a/d:prev/next, q/e: jump 10 steps, esc: quit")
  while not END:
    im_file = imdir_list[i]
    im = cv2.imread(str(im_file))
    win_name = "[%d/%d] " % (i, max_i) + str(im_file)
    cv2.namedWindow(win_name)
    lb_file_name = '.'.join(im_file.name.split('.')[:-1]) + ".txt"
    lb_file = lbdir / lb_file_name
    if lb_file in lbdir_list:
      bboxes = []
      with open(lb_file, 'r') as lb:
        for line in lb:
          bb = line.strip().split(' ')
          bb[0], bb[1:] = int(bb[0]), list(map(float, bb[1:]))
          bboxes.append(bb)
      draw_bbox(opt, im, bboxes)
    else:
      bbox_txt = r"* box label not found *"
      cv2.putText(im, bbox_txt, (5,18), 0, 0.6, (0,0,255),1)

    cv2.moveWindow(win_name, opt.window[0], opt.window[1])
    if opt.imgsz:
      h, w, _ = im.shape
      scale = max(opt.imgsz[0] / w, opt.imgsz[1] / h)
      rh, rw = int(h * scale), int(w * scale)
      resize_txt = r"resize: %dx%d -> %dx%d (scale %.2f)" % (w,h,rw,rh,scale)
      cv2.putText(im, resize_txt, (5,40), 0, 0.6, (0,0,255),1)
      im = cv2.resize(im, (rw,rh))
    cv2.imshow(win_name, im)
    print(win_name)
    while True:
      k = cv2.waitKeyEx(0)
      if k == ord('a') or k == 0xFF51:
        i-=1
        break
      elif k == ord('d') or k == 0xFF53:
        i+=1
        break
      elif k == ord('q'):
        i-=10
        break
      elif k == ord('e'):
        i+=10
        break
      elif k == ord('1'):
        i-=100
        break
      elif k == ord('3'):
        i+=100
        break
      elif k == 27:
        END = True
        break
    cv2.destroyWindow(win_name)
    i = 0 if i < 0 else i
    i = max_i if i > max_i else i

def parse_opt():
  parser = argparse.ArgumentParser()
  parser.add_argument('--dataset', type=str, default='', help='dataset directory. here has to include "images" and "labels"')
  parser.add_argument('--images', type=str, default=ROOT / 'images', help='image file directory')
  parser.add_argument('--labels', type=str, default=ROOT / 'labels', help='yolo label file directory or coco json file')
  #parser.add_argument('--yolo', action='store_true', help='yolo label format') # default
  parser.add_argument('--coco', action='store_true', help='coco label format - TODO')
  parser.add_argument('--imgsz', nargs='+', type=int, default=[], help='display image size (w,h)')
  #parser.add_argument('--gray', action='store_true', help='read and display image as grayscale (rgb is default)')
  parser.add_argument('--window', nargs='+', type=int, default=[100, 100], help='x server window location')
  parser.add_argument('--roi', action='store_true', help='draw roi box with roi-margin option')
  parser.add_argument('--roi-margin', nargs='+', type=float, default=[2, .5, .5, .5, 0],
                      help='add roi_box. [cat #, left, right, up, bottom margin] per hand w,h [0,inf]')
  opt = parser.parse_args()
  return opt

if __name__ == "__main__":
  opt = parse_opt()
  main(opt)
  cv2.destroyAllWindows()
