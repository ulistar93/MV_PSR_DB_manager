# search current directory
# and find annotation json and image files
# Then, make a dataframe based on annotation json
# and macth image file locations in real
# This code assume that there is no two image file which has same name

from pycocotools.coco import COCO
import numpy as np
import json
import skimage.io as io
import pdb

#dataType='train2017'
print('load coco...')
t_annFile='./annotations/instances_train2017.json'
v_annFile='./annotations/instances_val2017.json'
out_annFile='./annotations/instances_all2017.json'
cocoT = COCO(t_annFile)
cocoV = COCO(v_annFile)

print('getCatIds...(filtering)')
#catIds = coco.getCatIds(catNms=['person','cell phone','toothbrush']);
catIdsT = cocoT.getCatIds(catNms=['cell phone'])
catIdsV = cocoV.getCatIds(catNms=['cell phone'])
assert catIdsT == catIdsV
catIds = catIdsT
print('done')

print('getImgIds...')
t_imgIds = cocoT.getImgIds(catIds=catIds)
v_imgIds = cocoV.getImgIds(catIds=catIds)
assert len(list(set(v_imgIds).intersection(t_imgIds))) == 0

print('getAnnIds...')
t_annIds = cocoT.getAnnIds(catIds=catIds)
v_annIds = cocoV.getAnnIds(catIds=catIds)
assert len(list(set(v_annIds).intersection(t_annIds))) == 0

imgsT = cocoT.loadImgs(t_imgIds)
for im in imgsT:
  im['file_name'] = 'train2017/' + im['file_name']
imgsV = cocoV.loadImgs(v_imgIds)
for im in imgsV:
  im['file_name'] = 'val2017/' + im['file_name']
new_imgs = imgsT + imgsV

annsT = cocoT.loadAnns(t_annIds)
annsV = cocoV.loadAnns(v_annIds)
new_anns = annsT + annsV

with open(v_annFile, 'r') as f:
  v_anno_js = json.load(f)
new_info = v_anno_js['info']
new_licen = v_anno_js['licenses']
new_cat = v_anno_js['categories']

new_anno_dict = {'info':new_info,
                 'licenses':new_licen,
                 'images':new_imgs,
                 'annotations':new_anns,
                 'categories':new_cat}

print('json.dump...')
with open(out_annFile, 'w') as f:
  json.dump(new_anno_dict, f)
print('done')

pdb.set_trace()
pass

