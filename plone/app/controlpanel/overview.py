from plone.memoize.instance import memoize

from Acquisition import aq_base
from Acquisition import aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.controlpanel.form import ControlPanelView


def three_column_list(input_list):
    list_len = len(input_list)

    # Calculate the length of the sublists
    sublist_len = (list_len % 3 == 0 and list_len / 3 or list_len / 3 + 1)

    # Calculate the list end point given the list number
    def _list_end(num):
        return (num == 2 and list_len or (num + 1) * sublist_len)

    # Generate only filled columns
    final = []
    for i in range(3):
        column = input_list[i*sublist_len:_list_end(i)]
        if len(column) > 0:
            final.append(column)
    return final


class OverviewControlPanel(ControlPanelView):

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
        return mt.needUpgrading()

    def mailhost_warning(self):
        mailhost = getToolByName(aq_inner(self.context), 'MailHost', None)
        if mailhost is None:
            return True
        mailhost = getattr(aq_base(mailhost), 'smtp_host', None)
        email = getattr(aq_inner(self.context), 'email_from_address', None)
        if mailhost and email:
            return False
        return True

    def categories(self):
        return self.cptool().getGroups()

    def sublists(self, category):
        actions = self.cptool().enumConfiglets(group=category)
        return three_column_list(actions)
