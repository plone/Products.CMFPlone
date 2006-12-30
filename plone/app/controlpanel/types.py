from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Int
from zope.schema import Tuple
from zope.schema import TextLine

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from Products.Archetypes.mimetype_utils import getDefaultContentType, \
    setDefaultContentType, getAllowedContentTypes, getAllowableContentTypes, \
    setForbiddenContentTypes

from form import ControlPanelForm
from widgets import AllowedTypesWidget

class ITypesSchema(Interface):

    default_type = Choice(title=_(u'Default Format'),
        description=_(u'''Select the default format of textfields 
            for newly created content objects.'''),
        default=u'text/html',
        missing_value=set(),
        vocabulary="plone.app.vocabularies.AllowableContentTypes",
        required=True)

    allowed_types = Tuple(title=_(u'Alternative Formats'),
        description=_(u'''Select which formats are available for users 
            as alternative to the default format. Note that if new formats are
            installed, they will be enabled for text fields by default unless
            explicitly turned off here or by the relevant installer.'''),
        required=True,
        missing_value=set(),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.AllowableContentTypes"))


class TypesControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(ITypesSchema)

    def __init__(self, context):
        super(TypesControlPanelAdapter, self).__init__(context)
        self.context = context

    def get_default_type(self):
        return getDefaultContentType(self.context)

    def set_default_type(self, value):
        setDefaultContentType(self.context, value)

    default_type = property(get_default_type, set_default_type)

    def get_allowed_types(self):
        return getAllowedContentTypes(self.context)

    def set_allowed_types(self, value):
        # The menu pretends to be a whitelist, but we are storing a blacklist so that
        # new types are available by default. So, we inverse the list.
        allowable_types = getAllowableContentTypes(self.context)
        forbidden_types = [t for t in allowable_types if t not in value]
        setForbiddenContentTypes(self.context, forbidden_types)

    allowed_types = property(get_allowed_types, set_allowed_types)


class TypesControlPanel(ControlPanelForm):

    form_fields = FormFields(ITypesSchema)
    form_fields['allowed_types'].custom_widget = AllowedTypesWidget

    label = _("Type settings")
    description = _('''Lets you set the default Mimetype for TextFields and configure the list of
        user-selectable alternatives to that default.''')
    form_name = _("Type settings")
