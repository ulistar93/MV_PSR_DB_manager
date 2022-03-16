# search current directory
# and find annotation json and image files
# Then, make a dataframe based on annotation json
# and macth image file locations in real
# This code assume that there is no two image file which has same name

import json
import pandas as pd
import numpy as np
import copy
import pickle
from pathlib import Path
from pytools.uinputs import Input
import pdb

if __name__ == "__main__":
  p = path('.')
  support_img_formats = ['png', 'jpg', 'jpeg', 'bmp']
  all_img_list = []
  for img_fm in support_img_formats:
    all_img_list += list(p.rglob('*.'+img_fm))
  all_anno_list = list(p.rglob('instances_*.json'))

  for anno_path in all_anno_list:
    with open(anno_path, 'r') as f:
      print("* read anno %s *" % str(anno_path))
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

      anno
  anno_db
  for img in all_img_list:
    find_img()
  def read_dir(self):
    im_df = pd.DataFrame()
    an_df = pd.DataFrame()
    ct_df = pd.DataFrame()
    p = Path(self.sdir)
    lprint("* finding anno files instances_*.json *")
    anno_flist = list(p.rglob('instances_*.json'))
    lprint("* anno file list = %s *" % str(anno_flist))
    img_dlist = []
    for anno_file in anno_flist:
      #lprint(anno_file)
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
        lprint("* read anno %s *" % anno_file)
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

import datetime
def lprint(_str):
  _str = str(_str)
  dt = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
  print("[%s db] " % dt + _str)

class DB:
  def __init__(self, _sdir=''):
    self.sdir = _sdir
    self.amiex = False
    self.img_df = None
    self.anno_df = None
    self.cat_df = None
    self.anno_flist = []
    if _sdir: # if _sdir != ''
      _pkl_file = self.check_pkl_exist()
      if _pkl_file.exists():
        #self.img_df, self.anno_df, self.cat_df = self.load_pkl(_pkl_file)
        lprint("* Find pickle file -> load_pkl %s *" % _pkl_file)
        self.load_pkl(_pkl_file)
      else:
        #self.img_df, self.anno_df, self.cat_df = self.read_dir()
        lprint("* No pickle file exist -> read_dir *")
        self.read_dir()
        self.save_pkl(_pkl_file)

  def check_pkl_exist(self):
    p = Path(self.sdir)
    #pdb.set_trace()
    #pkls = list(p.glob('db.pkl'))
    pkls = list(p.glob('*.pkl'))
    if len(pkls) == 0:
      lprint("* There is no pickle. create new db.pkl. *")
      return p / 'db.pkl'
    elif p/'db.pkl' not in pkls:
      pkls_str = ''
      pkls_i = 1
      for x in pkls:
        pkls_str += str(pkls_i) + ': ' + str(x) + '\n'
        pkls_i += 1
      pkls.append(p/'db.pkl')
      pkls_str += str(pkls_i) + ': (new) ' + str(pkls[-1]) + '\n'
      pkl_idx = int(Input('tx',"* There is no default pickle (db.pkl). Which one do you want? * \n" + pkls_str, '[default=%d]' % pkls_i))
      return pkls[pkl_idx - 1]
    elif len(pkls) == 1:
      return pkls[0]
    elif len(pkls) > 1:
      pkls_str = ''
      pkls_i = 1
      for x in pkls:
        pkls_str += str(pkls_i) + ': ' + str(x) + '\n'
        pkls_i += 1
      pkl_idx = int(Input('tx',"* There are multiple pickles. Which one do you want? * \n" + pkls_str, '[default=1]'))
      return pkls[pkl_idx - 1]
    else: #len(pkls) == 0
      return ''

  def read_dir(self):
    im_df = pd.DataFrame()
    an_df = pd.DataFrame()
    ct_df = pd.DataFrame()
    p = Path(self.sdir)
    lprint("* finding anno files instances_*.json *")
    anno_flist = list(p.rglob('instances_*.json'))
    lprint("* anno file list = %s *" % str(anno_flist))
    img_dlist = []
    for anno_file in anno_flist:
      #lprint(anno_file)
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
        lprint("* read anno %s *" % anno_file)
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

  def save_pkl(self, _pkl_file):
    lprint("* %s pickle saving ... *" % str(_pkl_file))
    if _pkl_file.exists():
      if Input('yn',"* %s already exist. Do you want to overwrite ? *" % str(_pkl_file), "[y/N]"):
        pass
      else:
        lprint("** abort the db pkl save **")
        return
    with open(_pkl_file,'wb') as f:
      pickle.dump(self,f)

  def load_pkl(self, pkl_file):
    #pdb.set_trace()
    with open(pkl_file, 'rb') as f:
      r_db = pickle.load(f)
    assert self.sdir == r_db.sdir
    # TODO - distinguish db.pkl vs ex_db.pkl
    # because of img,anno df index
    #if r_db.amiex:
    #  r_db.clean_ex()
    self.amiex = r_db.amiex
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

  def clean_ex(self):
    lprint("* This db is ex_db -> clean_ex *")
    #self.img_df
    #Index(['id', 'width', 'height', 'file_name', 'license', 'flickr_url',
    #   'coco_url', 'date_captured', 'anno_file', 'full_path', 'new_id', 'tv',
    #   'new_file_name', 'new_full_path'],
    #  dtype='object')
    #
    #self.anno_df
    #Index(['id', 'image_id', 'category_id', 'segmentation', 'area', 'bbox',
    #   'iscrowd', 'attributes', 'anno_file', 'new_id', 'new_image_id', 'common_cat_id',
    #   'tv'],
    #  dtype='object')
    #
    #self.cat_df 
    #Index(['id', 'name', 'supercategory', 'anno_file', 'common_cat_id'], dtype='object')
    #
    # self.sdir = './tsr'
    # x = PosixPath('results/Lasvegas Taxi 2/task_2018060...
    #
    sp = Path(self.sdir)
    self.anno_flist = [ x for x in self.anno_flist if sp in x.parents]

    self.img_df = self.img_df.drop(['id', 'file_name', 'full_path', 'tv', 'anno_file'], axis=1)
    self.img_df.rename({'new_id':'id', 'new_file_name':'file_name', 'new_full_path':'full_path'}, axis=1, inplace=True)
    self.anno_df = self.anno_df.drop(['id', 'image_id', 'category_id', 'tv', 'anno_file'], axis=1)
    self.anno_df.rename({'new_id':'id', 'new_image_id':'image_name', 'common_cat_id':'category_id'}, axis=1, inplace=True)
    pdb.set_trace()
    self.cat_df = self.cat_df.drop(['id', 'anno_file'], axis=1)
    self.cat_df.rename({'common_cat_id':'id'}, axis=1, inplace=True)
    #pdb.set_trace()
    self.amiex = False
    pdb.set_trace()

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
              lprint("** there is no category %s **" % lb)
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
              lprint("** there is no category %s **" % lb)
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
        lprint("** wrong extractor **")
        return
    update_an_df.reset_index(inplace = True)
    update_im_df.reset_index(inplace = True)
    update_ct_df.reset_index(inplace = True)
    self.anno_df = update_an_df
    self.img_df = update_im_df
    self.cat_df = update_ct_df
    return

  def make_json(self):
    pass

  def pdb_display(self):
    img_df = self.img_df
    anno_df = self.anno_df
    cat_df = self.cat_df
    anno_flist = self.anno_flist
    if self.amiex:
      anno_cid_key = 'common_cat_id'
      anno_imid_key = 'new_image_id'
      cat_cid_key = 'common_cat_id'
    else:
      anno_cid_key = 'category_id'
      anno_imid_key = 'image_id'
      cat_cid_key = 'id'

    img_df['annos'] = [pd.NA] * len(img_df)
    img_df['cats'] = [pd.NA] * len(img_df)

    cat_set = set(self.cat_df.name)
    cat_list = list(cat_set)
    cat_id_list = []
    for c in cat_list:
      #cat_id_list.append(int(cat_df[cat_df['name'] == c].common_cat_id.iloc[0]))
      cat_id_list.append(int(cat_df[cat_df['name'] == c][cat_cid_key].iloc[0]))
    #pdb.set_trace()
    for cid, cname in zip(cat_id_list, cat_list):
      #c_an_df = anno_df[anno_df['common_cat_id']==cid]
      c_an_df = anno_df[anno_df[anno_cid_key]==cid]
      #lprint("cat %d, %s, #img= %d"%(cid,cname,len(set(c_an_df.new_image_id))))
      lprint("cat %d, %s, #img= %d"%(cid,cname,len(set(c_an_df[anno_imid_key]))))
      attrs = c_an_df.iloc[0].attributes.keys()
      for at in attrs:
        if at in ['Color','Velocity']:
          at_case = []
          for _, an in c_an_df.iterrows():
            if an.attributes[at] not in at_case:
              at_case.append(an.attributes[at])
          at_case.sort()
          lprint("  attr %s has %s cases" % (at, str(at_case)))
          #pdb.set_trace()
          for att in at_case:
            att_imgidset = set()
            for _, an in c_an_df.iterrows():
              if an.attributes[at] == att:
                #att_imgidset.add(an.new_image_id)
                att_imgidset.add(an[anno_imid_key])
            lprint("attr %s == %s in %s, #img= %d" % (at, att, cname, len(att_imgidset)))
        else:
          continue
      #pdb.set_trace()
#    lprint("* img-anno matching *")
#    def img_anno_match(an_df):
#      # TODO - new_id -> id
#      im = img_df[img_df['new_id'] == an_df['new_image_id']]
#      if type(im['annos']) == list:
#        im['cats'].append(an_df['common_cat_id'])
#      else:
#        #im['annos'] = [an_df['id?']] # there is no anno_df's new_id
#        im['cats'] = [an_df['common_cat_id']]
#
#    _ = anno_df.apply(img_anno_match, axis=1)
    lprint("* pdb_display End *")
    pdb.set_trace()
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
      lprint("** there is no table to show -> abort **")
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
    lprint("db['cate'].__repr__()")
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

