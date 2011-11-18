from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from form import ControlPanelForm
from widgets import DropdownChoiceWidget

from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

ICON_VISIBILITY_CHOICES = {
    _(u"Only for users who are logged in"): 'authenticated',
    _(u"Never show icons"): 'disabled',
    _(u"Always show icons"): 'enabled',
}

ICON_VISIBILITY_VOCABULARY = SimpleVocabulary(
    [SimpleTerm(v, v, k) for k, v in ICON_VISIBILITY_CHOICES.items()]
    )


class ISkinsSchema(Interface):

    theme = Choice(title=_(u'Default theme'),
                  description=_(u'''Select the default theme for the site.'''),
                  required=True,
                  missing_value=tuple(),
                  vocabulary="plone.app.vocabularies.Skins")

    mark_special_links = Bool(title=_(u'Mark external links'),
                              description=_(u"If enabled all external links "
                                             "will be marked with link type "
                                             "specific icons."),
                              default=True)

    ext_links_open_new_window = Bool(title=_(u"External links open in new "
                                              "window"),
                                     description=_(u"If enabled all external "
                                                    "links in the content "
                                                    "region open in a new "
                                                    "window."),
                                     default=False)

    icon_visibility = Choice(title=_(u'Show content type icons'),
                             description=_(u"If disabled the content icons "
                                            "in folder listings and portlets "
                                            "won't be visible."),
                             vocabulary=ICON_VISIBILITY_VOCABULARY)

    use_popups = Bool(title=_(u'Use popup overlays for simple forms'),
                        description=_(u"If enabled popup overlays will be "
                                       "used for simple forms like login, "
                                       "contact and delete confirmation."),
                        default=True)


class SkinsControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISkinsSchema)

    def __init__(self, context):
        super(SkinsControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_skins')
        self.jstool = getToolByName(context, 'portal_javascripts')
        self.csstool = getToolByName(context, 'portal_css')
        self.ksstool = getToolByName(context, 'portal_kss')
        ptool = getToolByName(context, 'portal_properties')
        self.props = ptool.site_properties
        self.themeChanged = False

    def get_theme(self):
        return self.context.getDefaultSkin()

    def set_theme(self, value):
        self.themeChanged = True
        self.context.default_skin = value

    theme = property(get_theme, set_theme)

    def _update_jsreg_mark_special(self):
        self.jstool.getResource('mark_special_links.js').setEnabled(
            self.mark_special_links or self.ext_links_open_new_window
            )
        self.jstool.cookResources()

    def get_mark_special_links(self):
        msl = getattr(self.props, 'mark_special_links', False)
        if msl == 'true':
            return True
        return False

        # return self.jstool.getResource('mark_special_links.js').getEnabled()

    def set_mark_special_links(self, value):
        if value:
            mark_special_links='true'
        else:
            mark_special_links='false'
        if self.props.hasProperty('mark_special_links'):
            self.props.manage_changeProperties(mark_special_links=mark_special_links)
        else:
            self.props.manage_addProperty('mark_special_links', mark_special_links, 'string')
        self._update_jsreg_mark_special()

    mark_special_links = property(get_mark_special_links,
                                  set_mark_special_links)

    def get_ext_links_open_new_window(self):
        elonw = self.props.external_links_open_new_window
        if elonw == 'true':
            return True
        return False

    def set_ext_links_open_new_window(self, value):
        if value:
            self.props.manage_changeProperties(external_links_open_new_window='true')
        else:
            self.props.manage_changeProperties(external_links_open_new_window='false')
        self._update_jsreg_mark_special()

    ext_links_open_new_window = property(get_ext_links_open_new_window,
                                         set_ext_links_open_new_window)

    def get_icon_visibility(self):
        return self.props.icon_visibility

    def set_icon_visibility(self, value):
        self.props.manage_changeProperties(icon_visibility=value)

    icon_visibility = property(get_icon_visibility,set_icon_visibility)

    def get_use_popups(self):
        return self.jstool.getResource('popupforms.js').getEnabled()
        return self.csstool.getResource('++resource++plone.app.jquerytools.overlays.css').getEnabled()

    def set_use_popups(self, value):
        self.jstool.getResource('popupforms.js').setEnabled(value)
        self.jstool.cookResources()
        self.csstool.getResource('++resource++plone.app.jquerytools.overlays.css').setEnabled(value)
        self.csstool.cookResources()

    use_popups = property(get_use_popups, set_use_popups)


class SkinsControlPanel(ControlPanelForm):

    form_fields = FormFields(ISkinsSchema)
    form_fields['theme'].custom_widget = DropdownChoiceWidget

    label = _("Theme settings")
    description = _("Settings that affect the site's look and feel.")
    form_name = _("Theme settings")

    def _on_save(self, data=None):
        # Force a refresh of the page so that a new theme choice fully takes
        # effect.
        if not self.errors and self.adapters['ISkinsSchema'].themeChanged:
            self.request.response.redirect(self.request.URL)
