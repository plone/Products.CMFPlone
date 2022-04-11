from AccessControl import getSecurityManager
from AccessControl.Permissions import view_management_screens
from Acquisition import aq_inner
from App.config import getConfiguration
from plone.autoform.form import AutoExtensibleForm
from plone.base.interfaces import IMaintenanceSchema
from plone.base.utils import human_readable_size
from plone.memoize.view import memoize
from plone.protect import CheckAuthenticator
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.form import form
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer

import logging
import time


logger = logging.getLogger(__file__)

@implementer(IMaintenanceSchema)
class MaintenanceControlPanelAdapter:

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.maintenance_settings = registry.forInterface(
            IMaintenanceSchema, prefix="plone")

    def get_days(self):
        return self.maintenance_settings.days

    def set_days(self, value):
        self.maintenance_settings.days = value

    days = property(get_days, set_days)

class MaintenanceControlPanel(AutoExtensibleForm, form.EditForm):
    """A simple form to pack the databases."""

    schema = IMaintenanceSchema
    id = "maintenance-control-panel"
    label = _('Maintenance Settings')
    description = _("Zope server and site maintenance options.")
    form_name = _('Zope Database Packing')
    control_panel_view = "maintenance-controlpanel"
    template = ViewPageTemplateFile('maintenance.pt')

    @memoize
    def portal(self):
        portal_state = getMultiAdapter(
            (aq_inner(self.context), self.request),
            name='plone_portal_state')
        return portal_state.portal()

    @button.buttonAndHandler(_('Pack database now'), name='pack')
    def handle_pack_action(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        CheckAuthenticator(self.request)
        if not self.available():
            self.status = _(
                'text_not_allowed_manage_server',
                default='You are not allowed to manage the Zope server.'
            )
            return

        days = data.get('days', None)
        # skip the actual pack method in tests
        if days is not None and isinstance(days, int) and days >= 0:
            db = self.portal()._p_jar.db()
            t = time.time() - (days * 86400)
            db.pack(t)
        self.status = _('Packed the database.')

    def available(self):
        root = aq_inner(self.context).getPhysicalRoot()
        sm = getSecurityManager()
        return sm.checkPermission(view_management_screens, root)


    def isDevelopmentMode(self):
        return bool(getConfiguration().debug_mode)

    def coreVersions(self):
        mt = getToolByName(self.context, 'portal_migration')
        versions = mt.coreVersions()
        versions['Instance'] = versions['Plone Instance']
        return versions

    def dbName(self):
        return self.portal()._p_jar.db().database_name

    def dbSize(self):
        size = self.portal()._p_jar.db().getSize()
        return human_readable_size(size)
