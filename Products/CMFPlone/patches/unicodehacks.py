def _unicode_replace(structure):
    if isinstance(structure, str):
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


class FasterStringIO(list):
    """Append-only version of StringIO.
    """
    write = list.append

    def __init__(self, value=None):
        list.__init__(self)
        if value is not None:
            self.append(_unicode_replace(value))

    def getvalue(self):
        try:
            return u''.join(self)
        except UnicodeDecodeError:
            return u''.join([_unicode_replace(value) for value in self])
