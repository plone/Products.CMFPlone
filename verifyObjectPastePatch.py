from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore import CMFCorePermissions
from AccessControl import getSecurityManager
from Acquisition import aq_base, aq_inner, aq_parent

#Portions of this function were copy/pasted from CMFCore.PortalFolder of
#CMF 1.4.  This class is licensed under the ZPL 2.0 as stated here:
#http://www.zope.org/Resources/ZPL
#Zope Public License (ZPL) Version 2.0
#This software is Copyright (c) Zope Corporation (tm) and Contributors. All rights reserved.

def _verifyObjectPaste(self, object, validate_src=1):
    # XXX This is just an extension of a copy of the 
    # _verifyObjectPaste code from CMFCore's PortalFolder. 
    # Actually the missing check whether a content type is allowed 
    # to be pasted into another is a bug in CMFCore/PortalFolder.py.
    # Once this is corrected in CMFCore one can safely
    # remove this method (done probably in CMF 1.5).
    # http://plone.org/collector/2183

    # This assists the version in OFS.CopySupport.
    # It enables the clipboard to function correctly
    # with objects created by a multi-factory.
    securityChecksDone = 0
    if (hasattr(object, '__factory_meta_type__') and
        hasattr(self, 'all_meta_types')):
        mt = object.__factory_meta_type__
        method_name=None
        permission_name = None
        meta_types = self.all_meta_types
        if callable(meta_types): meta_types = meta_types()
        for d in meta_types:
            if d['name']==mt:
                method_name=d['action']
                permission_name = d.get('permission', None)
                break

        if permission_name is not None:
            if _checkPermission(permission_name,self):
                if not validate_src:
                    # We don't want to check the object on the clipboard
                    securityChecksDone = 1
                else:
                    try: parent = aq_parent(aq_inner(object))
                    except: parent = None
                    if getSecurityManager().validate(None, parent,
                                                     None, object):
                        # validation succeeded
                        securityChecksDone = 1
                    else:
                        raise 'Unauthorized', object.getId()
            else:
                raise 'Unauthorized', permission_name
        #
        # Old validation for objects that may not have registered 
        # themselves in the proper fashion.
        #
        elif method_name is not None:
            meth=self.unrestrictedTraverse(method_name)
            if hasattr(meth, 'im_self'):
                parent = meth.im_self
            else:
                try:    parent = aq_parent(aq_inner(meth))
                except: parent = None
            if getSecurityManager().validate(None, parent, None, meth):
                # Ensure the user is allowed to access the object on the
                # clipboard.
                if not validate_src:
                    securityChecksDone = 1
                else:
                    try: parent = aq_parent(aq_inner(object))
                    except: parent = None
                    if getSecurityManager().validate(None, parent,
                                                     None, object):
                        securityChecksDone = 1
                    else:
                        id = object.getId()
                        raise 'Unauthorized', id
            else:
                raise 'Unauthorized', method_name
    
    # call OFS's _verifyObjectPaste if necessary
    if not securityChecksDone:
        PortalFolder.inheritedAttribute(
            '_verifyObjectPaste')(self, object, validate_src)
    
    # check if CMF content type is allowed to be pasted
    type_name = getattr(aq_base(object), 'portal_type', None)
    if type_name is not None:
        pt = getToolByName(self, 'portal_types')
        myType = pt.getTypeInfo(self)
        if myType is not None and not myType.allowType(type_name):
            raise ValueError, \
                  "Disallowed to paste subobject type '%s'." % type_name

from Products.CMFCore.PortalFolder import PortalFolder
PortalFolder._verifyObjectPaste = _verifyObjectPaste
