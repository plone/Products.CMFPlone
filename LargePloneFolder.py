from Globals import InitializeClass
from PloneFolder import PloneFolder
from PloneFolder import factory_type_information as PloneFolder_fti
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base

# Pure laziness
factory_type_information={}
factory_type_information.update(PloneFolder_fti)
factory_type_information.update( {'id':'Large Plone Folder',
                                  'meta_type':'Large Plone Folder',
                                  'factory':'addLargePloneFolder'} )

class LargePloneFolder(BTreeFolder2Base, PloneFolder):
    meta_type='Large Plone Folder'

    def __init__(self, id, title=''):
        BTreeFolder2Base.__init__(self, id)
        PloneFolder.__init__(self, id, title)
        self.id=id
        self.title=title

    # as per CMFBTreeFolder.py
    def _checkId(self, id, allow_dup=0):
        PloneFolder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)

    manage_renameObject = PloneFolder.inheritedAttribute('manage_renameObject')

    # this works around a problem that makes empty folders
    # evaluate to false in boolean tests, like:
    # tal:condition="python: someFolder and someFolder.someMethod(...)"
    __len__ = PloneFolder.__len__

InitializeClass(LargePloneFolder)

def addLargePloneFolder(self, id, title='', description='', REQUEST=None):
    """ add a BTree-backed Plone Folder """
    obj = LargePloneFolder(id, title=title)
    obj.setDescription(description)
    self._setObject(id, obj)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

