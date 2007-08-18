from collections import deque

def _unicode_replace(structure):
    if isinstance(structure, str):
        text = structure.decode('utf-8')
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


class FasterStringIO(object):
    """Append-only version of StringIO, which ignores any initial buffer.

    Implemented by using an internal deque instead.
    """
    def __init__(self, buf=None):
        self.buf = buf = deque()
        self.bufappend = buf.append

    def close(self):
        self.buf.clear()

    def seek(self, pos, mode=0):
        raise RuntimeError("FasterStringIO.seek() not allowed")

    def write(self, s):
        self.bufappend(s)

    def getvalue(self):
        buf = self.buf
        try:
            result = u''.join(buf)
        except UnicodeDecodeError:
            result = u''.join([_unicode_replace(value) for value in buf])
        buf.clear()
        return result
