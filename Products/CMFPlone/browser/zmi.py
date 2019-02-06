# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.Five import BrowserView
from zope.location.interfaces import IRoot


class ZMIPatch(BrowserView):
    """Inject some links into the ZMI via patches/addzmiplonesite.py"""

    def __call__(self):
        self.is_plone_root = False
        self.is_zope_root = False

        if IPloneSiteRoot.providedBy(self.context):
            self.is_plone_root = True
        elif IRoot.providedBy(self.context):
            self.is_zope_root = True

        if self.is_plone_root:
            portal_migration = getToolByName(self.context, 'portal_migration')
            self.needs_upgrade = portal_migration.needUpgrading()
            self.url = self.context.absolute_url() + '@@plone-upgrade'
        return self.index()
