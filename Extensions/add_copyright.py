#!/usr/bin/python

## script to add copyright messages on .py and .pt files
## by Fabiano Weimar dos Santos <xiru@xiru.org>
## based on Andy McKay ClearWind script.

import os, sys

def notPresent(file, add):
    data = open(file, 'r').read()
    if data.find(add) > -1:
        print "Text already present in file", file
        return
    return data        

copytext = """\
##############################################################################
#
# Copyright (c) 2003 Alan Runyan, Alexander Limi and Contributors
#
# This software is subject to the provisions of the General Public License,
# Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""

def change_py(file):
    res = notPresent(file, copytext)
    if res is not None:
	res = copytext + res
        open(file, 'w').write(res)
        print "Changed", file

def change_pt(file):
    add = """\n<tal:comment replace="nothing">\n""" + copytext + """</tal:comment>\n"""

    res = notPresent(file, add)
    if res is not None:
        lines = res.split('\n')
        addlines = add.split('\n')
	if file.endswith('main_template.pt'):
	    res = lines[0:1] + addlines + lines[1:]
	else:
	    res = addlines + lines
        res = '\n'.join(res)
        open(file, 'w').write(res)
        print "Changed", file

def walker(ignore, dr, files):
    for file in files:
        file = os.path.join(dr, file)
        if file.endswith('.py'):
            change_py(file)
        if file.endswith('.pt'):
            change_pt(file)

if __name__=='__main__':
    os.path.walk(sys.argv[1], walker, [])
