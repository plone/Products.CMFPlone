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

InitializeClass(LargePloneFolder)

def addLargePloneFolder(self, id, title='', description='', REQUEST=None):
    """ add a BTree-backed Plone Folder """
    obj = LargePloneFolder(id, title=title)
    obj.setDescription(description)
    self._setObject(id, obj)
    if REQUEST is not None:
        REQUEST['RESPONSE'].redirect( sf.absolute_url() + '/manage_main' )

