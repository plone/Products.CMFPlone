from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope.schema import Bool
from zope.schema import Choice
from zope.site.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from form import ControlPanelForm


class IEditingSchema(Interface):

    visible_ids = Bool(title=_(u"Show 'Short Name' on content?"),
                       description=_(u"Display and allow users to edit the "
                           "'Short name' content identifiers, which form the "
                           "URL part of a content item's address. Once "
                           "enabled, users will then be able to enable this "
                           "option in their preferences."),
                       default=False,
                       required=False)

    default_editor = Choice(title=_(u'Default editor'),
                            description=_(u"Select the default wysiwyg editor. "
                                "Users will be able to choose their own or "
                                "select to use the site default."),
                            default=u'TinyMCE',
                            missing_value=set(),
                            vocabulary="plone.app.vocabularies.AvailableEditors",
                            required=False)

    ext_editor = Bool(title=_(u'Enable External Editor feature'),
                          description=_(u"Determines if the external editor "
                              "feature is enabled. This feature requires a "
                              "special client-side application installed. The "
                              "users also have to enable this in their "
                              "preferences."),
                          default=False,
                          required=False)

    enable_inline_editing = Bool(title=_(u"Enable inline editing"),
                                 description=_(u"Check this to enable "
                                                "inline editing on the site."),
                                 default=True,
                                 required=False)

    enable_link_integrity_checks = Bool(title=_(u"Enable link integrity "
                                                 "checks"),
                          description=_(u"Determines if the users should get "
                              "warnings when they delete or move content that "
                              "is linked from inside the site."),
                          default=True,
                          required=False)

    lock_on_ttw_edit = Bool(title=_(u"Enable locking for through-the-web edits"),
                          description=_(u"Disabling locking here will only "
                                "affect users editing content through the "
                                "Plone web UI.  Content edited via WebDAV "
                                "clients will still be subject to locking."),
                          default=True,
                          required=False)


class EditingControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IEditingSchema)

    def __init__(self, context):
        super(EditingControlPanelAdapter, self).__init__(context)
        self.portal = getSite()
        pprop = getToolByName(self.portal, 'portal_properties')
        self.context = pprop.site_properties
        self.encoding = pprop.site_properties.default_charset

    visible_ids = ProxyFieldProperty(IEditingSchema['visible_ids'])
    enable_inline_editing = ProxyFieldProperty(IEditingSchema['enable_inline_editing'])
    enable_link_integrity_checks = ProxyFieldProperty(IEditingSchema['enable_link_integrity_checks'])
    ext_editor = ProxyFieldProperty(IEditingSchema['ext_editor'])
    default_editor = ProxyFieldProperty(IEditingSchema['default_editor'])
    lock_on_ttw_edit = ProxyFieldProperty(IEditingSchema['lock_on_ttw_edit'])


class EditingControlPanel(ControlPanelForm):

    form_fields = form.FormFields(IEditingSchema)

    label = _("Editing settings")
    description = _("General editing settings.")
    form_name = _("Editing settings")
