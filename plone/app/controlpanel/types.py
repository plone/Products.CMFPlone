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

from Products.Archetypes.mimetype_utils import getDefaultContentType, setDefaultContentType

from form import ControlPanelForm


class ITypesSchema(Interface):

    default_type = Choice(title=_(u'Default Format'),
        description=_(u'''Select the default format of textfields 
            for newly created content objects.'''),
        default=u'text/html',
        missing_value=set(),
        vocabulary="AllowableContentTypes",
        required=True)

    # allowed_types = Tuple(title=_(u'Alternative Formats'),
    #     description=_(u'''Select which formats are available for users 
    #         as alternative to the default format.
    #         Note that if new formats are installed, they will be enabled for text fields by 
    #         default unless explicitly turned off here or by the relevant installer.'''),
    #     required=True,
    #     missing_value=set(),
    #     value_type=Choice(vocabulary="AllowableContentTypes"))


class TypesControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(ITypesSchema)

    def __init__(self, context):
        super(TypesControlPanelAdapter, self).__init__(context)
        self.context = context

#    allowed_types = ProxyFieldProperty(ITypesSchema['allowed_types'])
    def get_default_type(self):
        return getDefaultContentType(self.context)

    def set_default_type(self, value):
        setDefaultContentType(self.context, value)

    default_type = property(get_default_type, set_default_type)


class TypesControlPanel(ControlPanelForm):

    form_fields = FormFields(ITypesSchema)

    label = _("Types settings")
    description = _('''Lets you set the default Mimetype for TextFields and configure the list of
        user-selectable alternatives to that default.''')
    form_name = _("Types settings")

