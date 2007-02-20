from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Choice
from zope.schema import Tuple

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from form import ControlPanelForm
from widgets import DropdownChoiceWidget

class ISkinsSchema(Interface):

    theme = Choice(title=_(u'Default theme'),
                  description=_(u'''Select the default theme for the site.'''),
                  required=True,
                  missing_value=tuple(),
                  vocabulary="plone.app.vocabularies.Skins")


class SkinsControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISkinsSchema)

    def __init__(self, context):
        super(SkinsControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'portal_skins')

    def get_theme(self):
        return self.context.getDefaultSkin()

    def set_theme(self, value):
        self.context.default_skin = value

    theme = property(get_theme, set_theme)


class SkinsControlPanel(ControlPanelForm):

    form_fields = FormFields(ISkinsSchema)
    form_fields['theme'].custom_widget = DropdownChoiceWidget

    label = _("Theme setup")
    description = _("Settings that affect the site's look and feel.")
    form_name = _("Theme details")
