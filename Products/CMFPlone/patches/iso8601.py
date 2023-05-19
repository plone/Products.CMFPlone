# from warnings import warn
from DateTime import DateTime


def ISO(self):
    """return ISO8601 instead of ISO format, i.e. including the time zone.
    the latter shouldn't be used anymore.  please see
    http://dev.plone.org/plone/ticket/10140 for more info"""
    # Disable the warning until we fixed all of Plone Core.
    # warn('Calls to `DateTime.ISO()` should be replaced with '
    #      '`DateTime.ISO8601()` to avoid implicit changes to GMT in '
    #      'expressions like `DateTime(obj.ModificationTime())`.',
    #      DeprecationWarning, stacklevel=2)
    return self.ISO8601()


def applyPatches():
    DateTime.ISO = ISO
