from Products.CMFCore import CMFCorePermissions
from AccessControl import Permissions
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.Expression import Expression
from Acquisition import aq_base

import zLOG

def two03_two04(portal):
    """2.0.3 -> 2.0.4
    """
    out = []
    # No SMH on 2.0 branch
    #out += replaceMailHost(portal, out)
    
    return out

def replaceMailHost(portal, out):
    """replaces the mailhost with a secure mail host
    """
    id = 'MailHost'
    oldmh = getattr(aq_base(portal), id)
    title = oldmh.title
    smtp_host = oldmh.smtp_host
    smtp_port = oldmh.smtp_port
    
    if 'SecureMailHost' in portal.Control_Panel.objectIds():
        print portal.Control_Panel.objectIds()
        out.append('Removing old MailHost')
        portal.manage_delObjects([id])
    
        out.append('Adding new SecureMailHost: %s:%s' % (smtp_host, smtp_port))
        addMailhost = portal.manage_addProduct['SecureMailHost'].manage_addMailHost
        addMailhost(id, title=title, smtp_host=smtp_host, smtp_port=smtp_port)
    
    else:
        out.append(['Error: SecureMailHost not installed.', zLOG.ERROR])

    return out
