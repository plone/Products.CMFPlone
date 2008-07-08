from StringIO import StringIO
import textwrap
import warnings
from zope.tal.talinterpreter import _write_ValueError

def _unicode_replace(structure):
    if isinstance(structure, str):
        try:
            text = structure.decode('utf-8')
        except UnicodeDecodeError:
            # XXX Maybe, raise an exception here instead of a warning?
            warnings.warn(textwrap.dedent('''\

            *** *** Insertion of non-unicode non-ascii non-utf8 encoded text in TAL is deprecated and will be broken in Plone 4.0 !!!

            %s...
            ''' % (repr(structure), )), DeprecationWarning, 2)
            # XXX the next line is fool-proof and will substitute ??-s if the encoding was not
            # unicode
            text = structure.decode('utf-8', 'replace')
    else:
        text = unicode(structure)
    return text


def _nulljoin(valuelist):
    try:
        return u''.join(valuelist)
    except UnicodeDecodeError:
        pass
    return u''.join([_unicode_replace(value) for value in valuelist])


def new__call__(self, econtext):
    try:
        return self._expr % tuple([var(econtext) for var in self._vars])
    except UnicodeDecodeError:
        pass
    return self._expr % tuple([_unicode_replace(var(econtext)) for var in self._vars])


class FasterStringIO(StringIO):
    """Append-only version of StringIO, which ignores any initial buffer.

    This let's us have much faster write() and getvalue methods.

    Most of this code was taken from zope.tal.talinterpreter.py licenced under
    the ZPL 2.1.
    """
    def __init__(self, buf=None):
        self.buf = u''
        self.len = 0
        self.buflist = []
        self.bufappend = self.buflist.append
        self.pos = 0
        self.closed = False
        self.softspace = 0

    def close(self):
        if not self.closed:
            self.write = _write_ValueError
            StringIO.close(self)

    def seek(self, pos, mode=0):
        raise RuntimeError("FasterStringIO.seek() not allowed")

    def write(self, s):
        self.bufappend(s)
        self.len = self.pos = self.pos + len(s)

    def getvalue(self):
        if self.buflist:
            try:
                self.buf = u''.join(self.buflist)
            except UnicodeDecodeError:
                self.buf = u''.join([_unicode_replace(value) for value in self.buflist])
            self.buflist = []
        return self.buf
