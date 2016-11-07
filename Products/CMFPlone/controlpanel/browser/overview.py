# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Globals import DevelopmentMode
from plone.app.registry.browser import controlpanel
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility


class OverviewControlPanel(controlpanel.RegistryEditForm):

    template = ViewPageTemplateFile('overview.pt')

    base_category = 'controlpanel'
    ignored_categories = ('controlpanel_user')

    def __call__(self):
        self.request.set('disable_border', 1)
        return self.template()

    @memoize
    def cptool(self):
        return getToolByName(aq_inner(self.context), 'portal_controlpanel')

    @memoize
    def migration(self):
        return getToolByName(aq_inner(self.context), 'portal_migration')

    @memoize
    def core_versions(self):
        return self.migration().coreVersions()

    def pil(self):
        return 'PIL' in self.core_versions()

    def version_overview(self):

        core_versions = self.core_versions()
        versions = [
            'Plone %s (%s)' % (core_versions['Plone'],
                               core_versions['Plone Instance'])]

        for v in ('CMF', 'Zope', 'Python'):
            versions.append(v + ' ' + core_versions.get(v))
        pil = core_versions.get('PIL', None)
        if pil is not None:
            versions.append('PIL ' + pil)
        return versions

    def is_dev_mode(self):
        return bool(DevelopmentMode)

    def upgrade_warning(self):
        mt = getToolByName(aq_inner(self.context), 'portal_migration')
        if mt.needUpgrading():
            # if the user can't run the upgrade, no sense in displaying the
            # message
            sm = getSecurityManager()
            if sm.checkPermission(ManagePortal, self.context):
                return True
        return False

    def mailhost_warning(self):
        registry = getUtility(IRegistry)
        mail_settings = registry.forInterface(
            IMailSchema, prefix='plone', check=False)
        mailhost = mail_settings.smtp_host
        email = mail_settings.email_from_address
        return not(mailhost and email)

    def timezone_warning(self):
        """Returns true, if the portal_timezone is not set in the registry.
        """
        # check if 'plone.portal_timezone' is in registry
        registry = getUtility(IRegistry)
        reg_key = "plone.portal_timezone"
        if reg_key not in registry:
            # else use 'plone.app.event.portal_timezone'
            # < Plone 5
            reg_key = 'plone.app.event.portal_timezone'
        if reg_key not in registry:
            return True
        portal_timezone = registry[reg_key]
        return not bool(portal_timezone)

    def categories(self):
        return self.cptool().getGroups()

    def sublists(self, category):
        return self.cptool().enumConfiglets(group=category)
