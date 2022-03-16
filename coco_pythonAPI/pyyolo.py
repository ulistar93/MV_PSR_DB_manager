import os
import pathlib
import numpy as np
import cv2
import json
import pathlib
import time
import copy
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

class YTS:
    def __init__(self, tsdata_file=None, data_dir=None):
      self.data_dir = data_dir
      self.cats = {}
      self.imgIds = []
      self.imgcacheId = []
      self.imgcache = []

      print('loading annotations into memory...')
      tic = time.time()
      if not tsdata_file == None:
        with open(tsdata_file) as f:
          for line in f:
            v, t = line.strip().split(' = ')
            if 'classes' in v:
              self.num_classes = int(t)
            elif 'names' in v:
              _names_file = t
        with open(_names_file) as fn:
          _id = 1
          for line in fn:
            name = line.strip()
            self.cats[_id] = name
            _id+=1
      if not self.data_dir == None:
        _dataFiles = sorted(os.listdir(self.data_dir))
        self.imgIds = list([ x.split('.jpg')[0] for x in _dataFiles if '.jpg' in x ])
      print('DONE (t={:0.2f}s)'.format(time.time()- tic))

    #def getImgIds(self, catIds=[]):
    def getImgIds(self):
      ids = copy.deepcopy(self.imgIds)
      return ids

    def loadImg(self, imgIds):
      tic = time.time()
      _imgIds = imgIds if not type(imgIds) is str else [imgIds]
      for ids in _imgIds:
        _img_file = '{}/{}.jpg'.format(self.data_dir,ids)
        _img = cv2.imread(_img_file)
        _img_rgb = cv2.cvtColor(_img, cv2.COLOR_BGR2RGB)
        self.imgcache.append(_img_rgb)
        self.imgcacheId.append(ids)
      print('DONE (t={:0.2f}s)'.format(time.time()- tic))
      return self.imgcache if not type(imgIds) is str else self.imgcache[0]

    def yolo2pix(self, bbox_list, img_shape):
        dh, dw, _ = img_shape
        bx = dw*(bbox_list[0] - bbox_list[2]/2)
        bw = dw*bbox_list[2]
        by = dh*(bbox_list[1] - bbox_list[3]/2)
        bh = dh*bbox_list[3]
        return bx, by, bw, bh

    def getImgSize(self, imgId):
      if imgId in self.imgcacheId:
        idx = self.imgcacheId.index(imgId)
        _img = self.imgcache[idx]
        return _img.shape
      else:
        _img = self.loadImg(imgId)
        return _img.shape

    def getAnno(self, imgIds):
      res = []
      _imgIds = imgIds if not type(imgIds) is str else [imgIds]
      for ids in _imgIds:
        ann_file = '{}/{}.txt'.format(self.data_dir,ids)
        anno=[]
        with open(ann_file) as af:
          for line in af:
            cat_id, centerX, centerY, w, h = list(map(float, line.strip().split(' ')))
            bx, by, bw, bh = self.yolo2pix([centerX, centerY, w, h], self.getImgSize(ids))
            an = {"category_id":int(cat_id),"category_name":self.cats[int(cat_id)], "bbox": [bx, by, bw, bh]}
            anno.append(an)
        res.append(anno)
      return res if not type(imgIds) is str else res[0]

    def showAnns(self, anno):
      polys = []
      color = []
      ax = plt.gca()
      ax.set_autoscale_on(False)
      for an in anno:
        bx, by, bw, bh = an['bbox']
        poly = [[bx, by], [bx, by+bh], [bx+bw, by+bh], [bx+bw, by]]
        np_poly = np.array(poly) #.reshape((4,2))
        polys.append(Polygon(np_poly))
        c = (np.random.random((1, 3))*0.6+0.4).tolist()[0] # random color
        color.append(c)

      p = PatchCollection(polys, facecolor=color, linewidths=0, alpha=0.4)
      ax.add_collection(p)
      p = PatchCollection(polys, facecolor='none', edgecolors=color, linewidths=2)
      ax.add_collection(p)

    def getImgAnnoPair(self, imgIds):
      imgs = self.loadImg(imgIds)
      annos = self.getAnno(imgIds)
      assert len(imgs) == len(annos), "Error: the number of member is different"
      res_pair = []
      for i in range(len(imgs)):
        res_pair.append((imgs[i], annos[i]))
      return res_pair
