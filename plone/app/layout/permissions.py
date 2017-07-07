# -*- coding: utf-8 -*-
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles


security = ModuleSecurityInfo('plone.app.layout')

security.declarePublic('ShowToolbar')
ShowToolbar = 'Show Toolbar'
setDefaultRoles(ShowToolbar, ('Authenticated',))
