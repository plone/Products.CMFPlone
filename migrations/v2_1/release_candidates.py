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
    replaceMailHost(portal, out)
    
    return out.getvalue()

def replaceMailHost(portal, out):
    """replaces the mailhost with a secure mail host
    """
    id = 'MailHost'
    oldmh = getattr(aq_base(portal), id)
    title = oldmh.title
    smtp_host = oldmh.smtp_host
    smtp_port = oldmh.smtp_port
    print >>out, 'Removing old MailHost'
    portal.manage_delObjects([id])
    
    print >>out, 'Adding new MailHost(SecureMailHost): %s:%s' % (smtp_host, smtp_port)
    addMailhost = portal.manage_addProduct['SecureMailHost'].manage_addMailHost
    addMailhost(id, title=title, smtp_host=smtp_host, smtp_port=smtp_port)
