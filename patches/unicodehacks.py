from StringIO import StringIO
import textwrap
import warnings
from zope.tal.talinterpreter import _write_ValueError

def _unicode_replace(structure):
    if isinstance(structure, str):
        try:
            text = structure.decode('ascii')
        except UnicodeDecodeError:
            try:
                text = structure.decode('utf')
                warnings.warn(textwrap.dedent('''\

                *** *** Insertion of non-unicode non-ascii text in TAL is deprecated and will be broken in Plone 4.0 !!!

                %s...
                ''' % (repr(structure), )), DeprecationWarning, 2)
            except UnicodeDecodeError:
                # XXX Maybe, raise an exception here instead of a warning?
                warnings.warn(textwrap.dedent('''\

                *** *** Insertion of non-unicode non-ascii non-utf8 encoded text in TAL is deprecated and will be broken in Plone 3.5 !!!

                %s...
                ''' % (repr(structure), )), DeprecationWarning, 2)
                # XXX the next line is fool-proof and will substitute ??-s if the encoding was not
                # unicode
                text = structure.decode('utf', 'replace')
    else:
        text = unicode(structure)
    return text

def _nulljoin(valuelist):
    try:
        return ''.join(valuelist)
    except UnicodeDecodeError:
        text = u''
        for value in valuelist:
            text += _unicode_replace(value)
        return text


class FasterStringIO(StringIO):
    """Append-only version of StringIO.

    This let's us have a much faster write() method.

    Most of this code was taken from zope.tal.talinterpreter.py licenced under
    the ZPL 2.1.
    """
    def close(self):
        if not self.closed:
            self.write = _write_ValueError
            StringIO.close(self)

    def seek(self, pos, mode=0):
        raise RuntimeError("FasterStringIO.seek() not allowed")

    def write(self, s):
        #assert self.pos == self.len
        self.buflist.append(s)
        self.len = self.pos = self.pos + len(s)

    def getvalue(self):
        if self.buflist:
            try:
                self.buf += ''.join(self.buflist)
            except UnicodeDecodeError:
                for value in self.buflist:
                    self.buf += _unicode_replace(value)
            self.buflist = []
        return self.buf
