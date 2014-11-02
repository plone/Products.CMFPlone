from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition import aq_inner
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.registry.browser import controlpanel
from plone.memoize.instance import memoize
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

try:
    import plone.app.event  # nopep8
    HAS_PAE = True
except ImportError:
    HAS_PAE = False


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

    @memoize
    def is_dev_mode(self):
        qi = getToolByName(aq_inner(self.context), 'portal_quickinstaller')
        return qi.isDevelopmentMode()

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
        mailhost = getToolByName(aq_inner(self.context), 'MailHost', None)
        if mailhost is None:
            return True
        mailhost = getattr(aq_base(mailhost), 'smtp_host', None)
        email = getattr(aq_inner(self.context), 'email_from_address', None)
        if mailhost and email:
            return False
        return True

    def timezone_warning(self):
        """Returns true, if the portal_timezone is not set in the registry.
        """
        if not HAS_PAE:
            # No point of having a portal timezone configured without
            # plone.app.event installed.
            # TODO: Above applies to situation at time of writing. If other
            # datetimes outside plone.app.event use proper timezones too, the
            # HAS_PAE should be removed.
            return False
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
        if portal_timezone:
            return False
        return True  # No portal_timezone found.

    def categories(self):
        return self.cptool().getGroups()

    def sublists(self, category):
        return self.cptool().enumConfiglets(group=category)
