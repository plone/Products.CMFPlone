#
# Helper objects for the Plone test suite
#

# $Id: dummy.py,v 1.1.2.1 2004/03/22 14:47:48 shh42 Exp $

from OFS.SimpleItem import SimpleItem


class Dummy:
    '''General purpose dummy object'''

    def __init__(self, **kw):
        self.__dict__.update(kw)


class Item(SimpleItem):
    '''Dummy Item 
       First-class Zope object. Can be _setObject'ed.
    '''

    id = 'dummy'
    meta_type = 'Dummy Item'
    manage_before_delete_called = 0

    def __init__(self, id=None, title=None, **kw):
        self.__dict__.update(kw)
        if id is not None:
            self.id = id
        if title is not None:
            self.title = title

    def manage_beforeDelete(self, item, container):
        self.manage_before_delete_called = 1


class File:
    '''Dummy upload object 
       Used to fake uploaded files and images.
    '''

    __allow_access_to_unprotected_subobjects__ = 1
    filename = 'dummy.gif'
    headers = {}

    def __init__(self, filename=None, headers=None):
        if filename is not None:
            self.filename = filename
        if headers is not None:
            self.headers = headers

    def seek(*args): pass
    def tell(*args): return 1
    def read(*args): return 'file data'


class Error(Exception):
    '''Dummy exception'''


class Raiser(SimpleItem):
    '''Raises the stored exception when called'''

    exception = Error

    def __init__(self, exception=None):
        if exception is not None:
            self.exception = exception

    def __call__(self, *args, **kw):
        raise self.exception 

