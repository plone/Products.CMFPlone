import os
from StringIO import StringIO

default_line='''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'''

def prepend(file, line):
    _b=None

    _f=open(file, 'r')
    _contents=StringIO()
    if '<!DOCTYPE' == _f.read(100)[:9]:
        return 
    _f.seek(0)
    _contents.write( line+'\n')
    while 1:
        _b=_f.read(10000)
        if not _b:
            break
        _contents.write( _b)

    _f.close()
    _f=open(file, 'w')

    _contents.seek(0)
    while 1:
        _b=_contents.read(10000)
        if not _b:
            break
        print 'prepending to ' + file
        _f.write(_b)
    _f.close()
 
def cb_prepend(arg, directory, files):
    for file in files:
        if file[-3:] == '.pt':
            try:
                prepend(os.path.join(directory, file), default_line)
            except: pass #lame

if __name__=='__main__':
    fname = '*.pt'
    directory = 'D:\CVS\Products\CMFPlone\skins'

    os.path.walk(directory, cb_prepend, 'secret')
