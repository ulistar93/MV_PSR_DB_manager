# tsr.py

from pathlib import Path
import datetime
import re
import pdb

class TSR:
  def __init__(self, arg=None):
    if isinstance(arg, dict):
      self.init_from_dict(arg)
    elif isinstance(arg, Path):
      self.init_from_path(arg)
    elif arg == None:
      self.name = "TSR"
      self.path = ''
      self.date_created = ''
      self.plist = []
      self.num_project = 0
    else:
      raise TypeError('Wrong initialization of Class \'Project\'')

  def __repr__(self):
    return "name: %s\ndate_created: %s\nlen(plist): %d" % (self.name,self.date_created,len(self.plist))

  def init_from_dict(self, s_dic):
    self.name = s_dic['name'] #'TSR'
    self.path = s_dic['path']
    self.date_created = s_dic['date_created']
    _plist = []
    for p in s_dic['plist']:
      _plist.append(Project(p))
    self.plist = _plist
    self.num_project = len(self.plist)

  def init_from_path(self, sdir):
    self.name = 'TSR'
    self.path = str(sdir)
    self.date_created = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
    _plist = []
    _proj_candi = [ x for x in list(sdir.iterdir()) if x.is_dir() ]
    for pc in _proj_candi:
      _plist.append(Project(pc))
    self.plist = _plist
    self.num_project = len(self.plist)

class Project(TSR):
  def __init__(self, arg=None):
    if isinstance(arg, dict):
      self.init_from_dict(arg)
    elif isinstance(arg, Path):
      self.init_from_path(arg)
    elif arg == None:
      self.name = ''
      self.task_list = []
      self.num_task = 0
    else:
      pdb.set_trace()
      raise TypeError('Wrong initialization of Class \'Project\'')

  def __repr__(self):
    return "{name: %s, num_task: %d}" % (self.name,self.num_task)

  def init_from_dict(self, p_dic):
    # initialize from dictionary
    try:
      self.name = p_dic['name']
      _tlist = []
      for ts in p_dic['task_list']:
        _tlist.append(Task(ts))
      self.task_list = _tlist
      self.num_task = p_dic['num_task']
    except:
      print('input dict key doesn\'t match with Task class')
      exit(0)

  def init_from_path(self, p_path):
    self.name = p_path.name
    _tlist = []
    _task_candi = list(p_path.iterdir())
    for tc in _task_candi:
      if not tc.is_dir():
        continue
      else:
        _tlist.append(Task(tc))
    self.task_list = _tlist
    self.num_task = len(self.task_list)

class Task(Project):
  def __init__(self, arg=None):
    if isinstance(arg, dict):
      self.init_from_dict(arg)
    elif isinstance(arg, Path):
      self.init_from_path(arg)
    elif arg == None:
      self.path = ''
      self.name = ''
      self.shortname = ''
      #self.image_loc = Path()
      self.image_locs = []
      self.image_files = []
      self.anno_files = []
      #self.anno_file = ''
      self.num_image = 0
    else:
      raise TypeError('Wrong initialization of Class \'Task\'')

  def __repr__(self):
    return "{name: %s, shortname: %s, path: %s, # of images: %d, image_location: %s, anno_files: %s}" % (self.name,self.shortname,str(self.path),len(self.image_files),str(self.image_locs),str(self.anno_files))

  def init_from_dict(self, t_dic):
    # initialize from dictionary
    try:
      #self.anno_file = t_dic['anno_file']
      self.anno_files = t_dic['anno_files']
      self.image_files = t_dic['image_files']
      #self.image_loc = Path(t_dic['image_loc'])
      self.image_locs = t_dic['image_locs']
      self.name = t_dic['name']
      self.num_image = t_dic['num_image']
      self.path = t_dic['path']
      self.shortname = t_dic['shortname']
    except:
      print('** input dict key doesn\'t match with Task class **')
      pdb.set_trace() # TODO - 아직 anno_file's'로 안만들어서 이름 못찾음 -> 전부 수정 필요
      exit(0)

  def init_from_path(self, t_path):
    # read coco format
    # task_dir
    #  ├── anoatation
    #  │   └── instances_default.json
    #  └── images
    #      └── [folders]
    #          └── ...
    #              └── *.jpg, jpeg, png, bmp
    self.path = t_path
    self.name = t_path.name
    _anno_files = list(t_path.rglob('instances_*.json'))
    #_anno_file = _anno_files[0]
    #if len(_anno_files) > 1:
    #  print("** There are serveral annotation files more than 1 in a single Task **")
    #  # TODO - when devide dataset as train/test, two different annotation files and image directory will be exist in a single Task
    #  pdb.set_trace()

    _image_files_all = []
    #_image_loc = []
    _image_locs = []
    image_format_support = ['jpg', 'jpeg', 'png', 'bmp']
    for img_fmt in image_format_support:
      _image_files = list(t_path.rglob('*.'+img_fmt))
      _image_files.sort()
      for i in _image_files:
        if i.parent in _image_locs:
          pass
        else:
          _image_locs.append(i.parent)
      _image_files_all += _image_files
    #if len(_image_locs) > 1:
    #  print("** There are serveral separated image folders in a single Task **")
    #  print("** Image files' name will be changed as follow the first folder name **")
    #  pdb.set_trace()
    #else:
    #  pdb.set_trace()
    #  _image_loc = _image_loc[0]
    _image_loc = _image_locs[0]

    _name = str(_image_loc)
    if '/images/' in _name:
      _name = _name.split('/images/')[1]
      if 'train/' in _name or 'valid/' in _name:
        _name = '/'.join(_name.split('/')[1:])
    else:
      _name = ""
    # if no subdir in /images, the split()[1] might be empty or invalid
    # in order to integrate between old(/images/*.jpg) and new dataset, to do this
    _name = re.sub('[^a-zA-Z0-9_/\-]', '', _name)
    _name = _name.replace('-','_').replace('/', '-')

    self.shortname = _name
    self.anno_files = _anno_files
    self.image_locs = _image_locs
    self.image_files = _image_files_all
    self.num_image = len(self.image_files)

def json_encoder(o):
  if isinstance(o, TSR):
    return o.__dict__
  elif isinstance(o, Project):
    return o.__dict__
  elif isinstance(o, Task):
    return o.__dict__
  elif isinstance(o, Path):
    return str(o)
  raise TypeError('not JSON serializable')

#def json_decoder(o):
#  if '__PosixPath__' in o:
#    return Path(o['__PosixPath__'])

