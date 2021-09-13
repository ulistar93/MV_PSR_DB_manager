# uinputs.py 
# to be more compact and handle difficult customized interface
# improt cmd is recommanded

def yntest(message, default):
  '''
    message : display text
    default : string with [y/n] choices
    return : y -> T, n -> F
  '''
  redo_msg = ''
  while True:
    ans = input(redo_msg + message + ' ' + default + ': ')
    if ('y' in ans) or ('Y' in ans):
      return True
    elif ('n' in ans) or ('N' in ans):
      return False
    elif ans == '':
      if 'Y' in default:
        return True
      elif 'N' in default:
        return False
      else:
        print("** There is no default option. Please retry **")
    else:
      print("** There is wrong input. Please retry **")
    redo_msg = 're: '

def txtest(message, default_txt):
  '''
    message : display text
    default : return when in '' (empty string)
    return : input text list
  '''
  redo_msg = ''
  default = default_txt.split('[default=')[1][:-1]
  while True:
    ans = input(redo_msg + message + default_txt + '\nInput: ')
    if ans != '':
      return ans
    elif default != '': # ans == ''
      return default
    else: # ans == '' and default == ''
      print("** Default is empty. Please retry **")
    redo_msg = 're: '

def Input(ftype, message, default):
  if ftype == 'yn':
    return yntest(message, default)
  elif ftype == 'tx':
    return txtest(message,default)
  else:
    raise ValueError('Invalid type argument')
  return
