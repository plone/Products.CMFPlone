from Products.CMFCore import CMFCorePermissions
from AccessControl import Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Acquisition import aq_base
from Products.CMFPlone.migrations.migration_util import saveCloneActions, cleanupSkinPath
import zLOG
from StringIO import StringIO

def two0x_rc1(portal):
    """2.0.x -> 2.1.0rc1
    """
    out = StringIO()
    
    return out.getvalues()

