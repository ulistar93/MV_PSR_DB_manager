# db.py

import json
import pandas as pd
import numpy as np
import copy
import pickle
from pathlib import Path
from pytools.uinputs import Input
import pdb

class DB:
  def __init__(self, _sdir=''):
    self.sdir = _sdir
    self.img_df = None
    self.anno_df = None
    self.cat_df = None
    self.anno_flist = []
    if _sdir: # if _sdir != ''
      _pkl_file = self.check_pkl_exist()
      if _pkl_file:
        #self.img_df, self.anno_df, self.cat_df = self.load_pkl(_pkl_file)
        print("* Find pickle file -> load_pkl *")
        self.load_pkl(_pkl_file)
      else:
        #self.img_df, self.anno_df, self.cat_df = self.read_dir()
        print("* No pickle file exist -> read_dir *")
        self.read_dir()
        self.save_pkl(_sdir, 'db.pkl')

  def check_pkl_exist(self):
    #print("[%s] s_dir table file check" % datetime.datetime.now().strftime('%H:%M:%S'))
    p = Path(self.sdir)
    pkls = list(p.glob('*.pkl'))
    #pdb.set_trace()
    if len(pkls) > 1:
      pkl_file = Input('tx',"* There are multiple pickles. Which one do you want? * \n" + str(pkls), '')
    elif len(pkls) == 1:
      return pkls[0]
    else: #len(pkls) == 0
      return ''

  def read_dir(self):
    im_df = pd.DataFrame()
    an_df = pd.DataFrame()
    ct_df = pd.DataFrame()
    p = Path(self.sdir)
    print("* finding anno files instances_*.json *")
    anno_flist = list(p.rglob('instances_*.json'))
    img_dlist = []
    for anno_file in anno_flist:
      #print(anno_file)
      #pdb.set_trace()
      task_dir = anno_file.parent.parent
      img_dir = task_dir / 'images'
      # here we believe, 
      # task_dir
      #  ├── anoatation
      #  │   └── instances_*.json
      #  └─── images
      #      ├── train
      #      │   └── *.jpg, jpeg, png, bmp
      #      ├── valid
      #      │   └── *.jpg, jpeg, png, bmp
      #      or
      #      └── [folders]
      #          └── ...
      #              └── *.jpg, jpeg, png, bmp
      with open(anno_file, 'r') as f:
        print("* read anno %s *" % anno_file)
        anno_js = json.load(f)
        _im_df = pd.DataFrame(anno_js['images'])
        _an_df = pd.DataFrame(anno_js['annotations'])
        _ct_df = pd.DataFrame(anno_js['categories'])
        _im_df['anno_file'] = anno_file
        _an_df['anno_file'] = anno_file
        _ct_df['anno_file'] = anno_file

        def img_file_check(fname):
          img_file = img_dir / fname
          if img_file.exists():
            return img_file
          else:
            return None
        _im_df['full_path'] = _im_df['file_name'].map(img_file_check)

      im_df = im_df.append(_im_df, ignore_index=True)
      an_df = an_df.append(_an_df, ignore_index=True)
      ct_df = ct_df.append(_ct_df, ignore_index=True)
    self.img_df = im_df
    self.anno_df = an_df
    self.cat_df = ct_df
    self.anno_flist = anno_flist

  # 이게 필요한가?
  def save_pkl(self, _path, _fname):
    print("* %s pickle saving ... *" % str(_path))
    if not isinstance(_path, Path):
      _path = Path(_path)
    pkl_file = _path / _fname
    if pkl_file.exists():
      if Input('yn',"* %s already have %s file. Do you want to overwrite ? *" % (str(_path), _fname), "[y/N]"):
        pass
      else:
        print("** abort the db pkl save **")
        return
    with open(pkl_file,'wb') as f:
      pickle.dump(self,f)

  def load_pkl(self, pkl_file):
    #pdb.set_trace()
    if not Path(pkl_file).exists():
      print("** There is no named pickle %s -> aborted **"%pkl_file)
      exit(0)
    with open(pkl_file, 'rb') as f:
      r_db = pickle.load(f)
    assert self.sdir == r_db.sdir
    self.img_df = r_db.img_df
    self.anno_df = r_db.anno_df
    self.cat_df = r_db.cat_df
    self.anno_flist = r_db.anno_flist

  def __repr__(self):
    return str(self.__dict__)

  def copy(self):
    r_db = DB()
    r_db.sdir = self.sdir
    r_db.img_df = self.img_df.copy()
    r_db.anno_df = self.anno_df.copy()
    r_db.cat_df = self.cat_df.copy()
    r_db.anno_flist = copy.deepcopy(self.anno_flist)
    return r_db

  def extract(self, ext):
    update_im_df = pd.DataFrame()
    update_an_df = pd.DataFrame()
    update_ct_df = pd.DataFrame()
    if ext[0] == 'label':
      if ext[1] == 'in':
        for anno_file in self.anno_flist:
          _im_df_an = self.img_df[self.img_df['anno_file'] == anno_file]
          _an_df_an = self.anno_df[self.anno_df['anno_file'] == anno_file]
          _ct_df_an = self.cat_df[self.cat_df['anno_file'] == anno_file]
          #_im_df_an_new = pd.DataFrame()
          _an_df_an_new = pd.DataFrame()
          _ct_df_an_new = pd.DataFrame()
          # _ct_df_lb = _ct_df_an[_ct_df_an['name'].isin(ext[2:])] # TODO - isin?
          for lb in ext[2:]:
            _ct_df_lb = _ct_df_an[ _ct_df_an['name'] == lb ]
            if _ct_df_lb.empty:
              print("** there is no category %s **" % lb)
              pdb.set_trace()
              continue
            cat_id = int(_ct_df_lb['id'])
            _an_df_lb = _an_df_an[ _an_df_an['category_id'] == cat_id ]
            _ct_df_an_new = _ct_df_an_new.append(_ct_df_lb)
            _an_df_an_new = _an_df_an_new.append(_an_df_lb)
          # _an_df_new = _an_df_an[_an_df_an['category_id'].isin(_ct_df_lb['id'])] # TODO - isin?
          in_expr = "id in %s" % str(_an_df_an_new['image_id'].tolist())
          _im_df_an_new = _im_df_an.query(in_expr)
          # _im_df_new = _im_df_an[_im_df_an['id'].isin(_an_df_new['image_id'])] # TODO - isin?, ~isin?
          update_ct_df = update_ct_df.append(_ct_df_an_new)
          update_an_df = update_an_df.append(_an_df_an_new)
          update_im_df = update_im_df.append(_im_df_an_new)
      elif ext[1] == 'ex':
        # TODO - check function below
        for anno_file in self.anno_flist:
          #pdb.set_trace()
          _im_df_an = self.img_df[self.img_df['anno_file'] == anno_file]
          _an_df_an = self.anno_df[self.anno_df['anno_file'] == anno_file]
          _ct_df_an = self.cat_df[self.cat_df['anno_file'] == anno_file]
          for lb in ext[2:]:
            #pdb.set_trace()
            _ct_df_lb = _ct_df_an[ _ct_df_an['name'] == lb ]
            if _ct_df_lb.empty:
              print("** there is no category %s **" % lb)
              pdb.set_trace()
              continue
            cat_id = int(_ct_df_lb['id'])
            _ct_df_an = _ct_df_an[ _ct_df_an['name'] != lb ]
            _an_df_an = _an_df_an[ _an_df_an['category_id'] != cat_id ]
          #_im_df_lb = _im_df_an[ _im_df_an['id'] in _an_df_lb['image_id'].tolist() ]

          in_expr = "id in %s" % str(_an_df_an['image_id'].tolist())
          _im_df_an = _im_df_an.query(in_expr)
          update_ct_df = update_ct_df.append(_ct_df_an)
          update_an_df = update_an_df.append(_an_df_an)
          update_im_df = update_im_df.append(_im_df_an)
      else:
        print("** wrong extractor **")
        return
    self.anno_df = update_an_df
    self.img_df = update_im_df
    self.cat_df = update_ct_df
    return

  def make_json(self):
    pass

def label_extractor(t,elem):
  '''
  label_extractor(t,elem):
    - t: "in" or "out" type
    - elem: the labels which be included or excluded
    :return: lambda x
    x = category id ? - TODO
  '''
  if t == 'in':
    return lambda x: True if x in elem else False
  elif t == 'ex':
    return lambda x: False if x in elem else True

def size_extractor(t,w,h,eq):
  '''
  TODO
  size_extractor(t,w,h,eq):
  - t: "in" or "out" type
  - w, h: the labels which be included or excluded
  - eq: a string consist of (<, >, =) means inequality
  :return: lambda x
  x, y = img w and h
  '''
  if t == 'in':
    #return lambda x, y: True if x in elem else False
    return True
  elif t == 'ex':
    #return lambda x: False if x in elem else True
    return False

class DB_viewer:
  def __init__(self, tsr_table = None):
    if tsr_table == None:
      print("** there is no table to show -> abort **")
      exit(0)
    self.db = DB(tsr_table)
    self.tsr = tsr_table

  def interactive(self):
    db = self.db
    print("************************************************")
    print("**          pdb.set_trace() stop              **")
    print("**   & usage &                                **")
    print("** db = self                                  **")
    print("** db[] = img, anno, cat                      **")
    print("** db['img']  <- all image list               **")
    print("** db['anno'] <- all annotation list          **")
    print("** db['cate'] <- all category list            **")
    print("**  <- db .img .anno .cate also can use       **")
    print("**                                            **")
    print("**   & project task view &                    **")
    print("** db.p    <- db project list                 **")
    print("** db.p[0] <- project 0                       **")
    print("** db.p[0].t    <- task list of project 0     **")
    print("** db.p[0].t[0] <- task 0 of project 0        **")
    print("**  <- p and t also access img,anno,cate      **")
    print("** db.p[0]['img'] <- img list of project 0    **")
    print("** db.p[0].t[0]['cate']                       **")
    print("**  <- category list of task 0                **")
    print("**                                            **")
    print("**   & filtering &                            **")
    print("** db['img'].cat('Stop sing - Oct')           **")
    print("**  <- img list which has 'Stop sign - Oct'   **")
    print("** db['img'].cat(1)                           **")
    print("**  <- index also possible                    **")
    print("**  <- please refer 'cate'index also possible **")
    print("** db['anno'].cat(1)                          **")
    print("**  <- anno list also available               **")
    print("**                                            **")
    print("************************************************")
    pdb.set_trace()
    #do sth print
    print("db['cate'].__repr__()")
    print(db['cate'].__repr__())
    print()
    for i in range(1,db['cate'].num +1):
      for t in db.cat(i):
        print(t)
      #print(db['img'].cat(i))
      #print(db['anno'].cat(i))
    #db.p[0].t[0]['cate'].cat(0)
    #db.p[0].t[0]['cate'].cat(1)
    #db.p[0].t[0]['img'].cat(0)
    pdb.set_trace()
    pass

  def img_list():
    pass

  def cat(self, category):
    print()
    pass
    #return tsr['cat']

