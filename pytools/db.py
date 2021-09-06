# db.py

import json
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import pdb

class DB:
  def __init__(self, _sdir):
    self.sdir = _sdir
    self.anno_df, self.img_df = self.read_dir()

  def read_dir(self):
    an_df = pd.DataFrame()
    im_df = pd.DataFrame()
    p = Path(_sdir)
    anno_flist = list(p.rglob('instances_*.json'))
    img_dlist = []
    for anno_file in anno_flist:
      for anno_file_p01 if list(anno_file.parents())[:2]:
        if '/images' in list(anno_file_p01.iterdir()):
          img_dir = anno_file_p01 / 'images'
          if not img_dir.is_dir():
            img_dir = ''
  ###########################################
  ## TODO - HERE 2021.09.06
  ###########################################

  def __repr__(self):
    return self.img_df

#################################
## old ##

  def __init__(self, tsr_o, parent_level=0):
    if parent_level == 0:
      self.level = parent_level + 1
      self.level_name = 'TSR'
      self.name = tsr_o.name
      self.p = [ DB(p, parent_level=self.level) for p in tsr_o.plist ] # project list
      self.child = self.p
      #self.img, self.anno, self.cat = self.init_lists()
    elif parent_level == 1:
      self.level = parent_level + 1
      self.level_name = 'Project'
      self.name = tsr_o.name
      self.t = [ DB(t, parent_level=self.level) for t in tsr_o.task_list ] # task list
      self.child = self.t
    elif parent_level == 2:
      self.level = parent_level + 1
      self.level_name = 'Task'
      self.name = tsr_o.name
      self.child = []
    else:
      print("** DB level is too deeper than task -> abort **")
      exit(0)
    self.img, self.anno, self.cate = self.init_lists(tsr_o)
    # self.img = db_list(type=img)
    # self.anno = db_list(type=anno)
    # self.cate = [] # category list

  def __repr__(self):
    _str = [ "\'level\': %d" % self.level ]
    _str += [ "\'level_name\': \'%s\'" % self.level_name ]
    _str += [ "\'name\': \'%s\'" % self.name ]
    _str += [ "\'child\': %s" % str(self.child) ]
    if self.level == 3: # print task's img, anno, cat only
      _str += [ "\'img\': %s" % str(self.img) ]
      _str += [ "\'anno\': %s" % str(self.anno) ]
      _str += [ "\'cate\': %s" % str(self.cate) ]
    else: # project and tsr has sum of child -> hide printing to avoid duplicate printing
      _str += [ "\'img\': ..." ]
      _str += [ "\'anno\': ..." ]
      _str += [ "\'cate\': ..." ]
    _str = '{ '+', '.join(_str)+' }'
    return '\n'+_str+'\n'

  def init_lists(self,tsr_o):
    db_list = self.db_list
    _img = db_list(self, 'img', [])
    _anno = db_list(self, 'anno', [])
    _cate = db_list(self, 'cate', [])
    if self.child:
      for cdb in self.child: # child is [db_project or db_task] , cdb = p or t
        _img += cdb['img']
        _anno += cdb['anno']
        _cate += [ x for x in cdb['cate'] if x not in _cate ]
    else:
      # child empty <=> this db means "Task"
      # open the anno file usually named "instances_default.json"
      anno_file = Path(tsr_o.anno_file)
      if not anno_file.exists():
        print("** anno_file doesn't exist -> abort **")
        exit(0)
      else:
        with open(anno_file, 'r') as f:
          anno_js = json.load(f)
          _img = db_list(self, 'img', anno_js["images"])
          _anno = db_list(self, 'anno', anno_js["annotations"])
          _cate = db_list(self, 'cate', anno_js["categories"])
    return _img, _anno, _cate

  def __getitem__(self, key):
    if key is 'img':
      return self.img
    elif key is 'anno':
      return self.anno
    elif key is 'cate':
      return self.cate
    else:
      print("not %s key in db" % key)
      pass

  def cat(self, search_key):
    im_cat = self.img.cat(search_key)
    an_cat = self.anno.cat(search_key)
    return im_cat, an_cat

  class db_list:
    def __init__(self, parent_db, list_type, dlist):
      self.type = list_type # img or anno
      self.parent_db = parent_db # img or anno
      self.list = dlist
      self.num = len(dlist)

    def __repr__(self):
      _str = [ "\'type\': \'%s\'" % self.type ]
      _str += [ "\'parent_db\': <%s object at 0x%x>" % (str(type(self.parent_db)).split('\'')[1], id(self.parent_db)) ]
      _str += [ "\'list\': %s" % str(self.list) ]
      _str += [ "\'num\': %d" % self.num ]
      _str = '{ ' + ', '.join(_str) + ' }'
      return _str

    def __str__(self):
      _str = [ "\'type\': \'%s\'" % self.type ]
      _str += [ "\'parent_db\': <%s %s>" % (str(type(self.parent_db)).split('\'')[1], self.parent_db.name) ]
      _str += [ "\'list\': %s" % ("..." if self.list else "") ]
      _str += [ "\'num\': %d" % self.num ]
      _str = '{ ' + ', '.join(_str) + ' }'
      return _str

    def __add__(self, x):
      if type(x) == list:
        self.list += x
        self.num = len(self.list)
        return self
      elif self.type != x.type:
        print("** db_list cannot be added from different types **")
        return []
      else:
        self.list += x.list
        self.num = len(self.list)
        return self

    def __iter__(self):
      return iter(self.list)

    def cat(self, search_key):
      #pdb.set_trace()
      pd = self.parent_db
      cat_idx = 0
      if type(search_key) == str:
        # find key index
        for c in pd['cate'].list:
          if search_key == c['name']:
            cat_idx = c['id']
      elif type(search_key) == int:
        cat_idx = search_key
      else:
        print("** Wrong input for cat() -> return None **")
        return None
      if cat_idx == 0 or cat_idx > pd['cate'].num:
        return ""
      #img_id_list = []
      res = []
      if self.type == 'anno':
        for an in self.list:
          if an['category_id'] == cat_idx:
            res.append(an)
      elif self.type == 'img':
        img_id_set = set()
        for an in pd['anno'].list:
          if an['category_id'] == cat_idx:
            img_id_set.add(an['image_id'])
        img_id_list = list(img_id_set)
        img_id_list.sort()
        for img_id in img_id_list:
          for im in self.list:
            if im['id'] == img_id:
              res.append(im)
              break
      elif self.type == 'cate':
        for ct in self.list:
          if ct['id'] == cat_idx:
            res.append(ct)
      else:
        print("** no match db_list type for cat() -> abort **")
        exit(0)
      #pdb.set_trace()
      return pd.db_list(pd, self.type, res)

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

