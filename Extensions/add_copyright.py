#!/usr/bin/env python
## script to add copyright messages on .py and .pt files
## by Fabiano Weimar dos Santos <xiru@xiru.org>
## based on Andy McKay ClearWind script.
## Rewritten by Sidnei da Silva <sidnei@awkly.org>

__metaclass__ = type

import sys
from os import remove, rename
from os.path import join, walk, splitext, exists
#X#from xml.dom import minidom
#X#from xml.parsers.expat import ExpatError
from cStringIO import StringIO

class BaseChecker:

    def __init__(self, text, out=StringIO()):
        self.text = text

    def check(self, data):
        """Returns false if text is found in data"""
        if data.find(self.text) > -1:
            return False
        return True


class PythonChecker(BaseChecker):

    def check(self, data):
        """Returns false if text is found in data"""
        if super(PythonChecker, self).check(data):
            # Python Scripts should never make it
            # TODO We need a better check here
            if data.split('\n')[0].startswith('## '):
                return False
            if data.find('##parameters=') > -1:
                return False
            if data.startswith('#!'):
                return False
            return True
        return False

class PageTemplateChecker(BaseChecker):
    pass

class BaseProcessor:

    def __init__(self, text, out=StringIO()):
        self.text = text
        self.out = out

    def process(self, fname, data):
        return "%s\n%s" % (self.text, data)

class PythonProcessor(BaseProcessor):
    pass

class PageTemplateProcessor(BaseProcessor):

    def process(self, fname, data):
        start = data.find('</body>')
        if start > -1:
            data = "%s\n%s\n%s" % (data[:start], self.text, data[start:])
            return data
        return False


copyright = """\
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

ptcopyright = """\
<tal:copyright replace="nothing">
%s</tal:copyright>
""" % copyright

class Walker:

    def __init__(self, checkers, processors, dry=False,
                 ignore=None, out=StringIO()):
        self.checkers = checkers
        self.processors = processors
        self.out = out
        self.dry = dry
        if ignore is None:
            ignore = {}
        self.ignore = ignore
        self.ignored = []
        self.processed = []
        self.failed = []

    def read(self, fname):
        try:
            f = open(fname, 'r')
            data = f.read()
            f.close()
            return data
        except IOError, msg:
            print >> self.out, "%s: I/O Error: %s" % (fname, str(msg))
        return None

    def write(self, fname, data):
        bak = fname + ".bak"
        if exists(bak):
            remove(bak)
        rename(fname, bak)
        print >> self.out, "Renamed %s to %s" % (fname, bak)
        try:
            f = open(fname, 'w')
            f.write(data)
            f.close()
            return True
        except IOError, msg:
            print >> self.out, "%s: I/O Error: %s" % (fname, str(msg))
        return None

    def walk(self, ignore, _dir, fnames):
        for fname in fnames:
            ext = splitext(fname)[-1]
            name = join(_dir, fname)
            ignore = self.ignore.get(ext)
            if ignore:
                self.ignored.append(name)
                continue
            checker = self.checkers.get(ext)
            if checker is None:
                self.ignore[ext] = True
                print >> out, ("Checker not found for '%s'. "
                               "Ignoring all remaining occurrences."
                               % ext)
                self.ignored.append(name)
                continue
            processor = self.processors.get(ext)
            if processor is None:
                self.ignore[ext] = True
                print >> out, ("Processor not found for '%s'. "
                               "Ignoring all remaining occurrences."
                               % ext)
                self.ignored.append(name)
                continue
            data = self.read(name)
            if data is None:
                self.failed.append(name)
                continue
            if checker.check(data):
                newdata = processor.process(name, data)
                if newdata:
                    # If dry is true, we just skip write
                    res = (not self.dry) and self.write(name, newdata) or True
                    if res:
                        self.processed.append(name)
                        print >> out, ("Processing of '%s' succeeded."
                                       % name)
                        continue
                else:
                    print >> out, ("Processor failed for '%s'."
                                   % name)
            self.failed.append(name)

if __name__=='__main__':
    out = StringIO()

    checkers = {'.pt':PageTemplateChecker(copyright, out),
                '.py':PythonChecker(copyright, out)}
    processors = {'.pt':PageTemplateProcessor(ptcopyright, out),
                  '.py':PythonProcessor(copyright, out)}

    walker = Walker(checkers, processors, dry=False, out=out)
    walk(sys.argv[1], walker.walk, [])
    total = len(walker.ignored) + len(walker.processed)
    print out.getvalue()
    print "Processed %s out of %s files" % (len(walker.processed), total)
