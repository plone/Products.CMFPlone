from plone.fieldsets import FormFieldsets

from zope.interface import Interface
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Int
from zope.schema import Password
from zope.schema import TextLine
from zope.schema import List
from zope.schema import Tuple

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr

from form import ControlPanelForm

class IFilterTagsSchema(Interface):

    nasty_tags = List(title=_(u'Nasty tags'),
                         description=_(u'''These tags, and their content are completely blocked
                             when a page is save or rendered.'''),
                         default=[u'applet', u'embed', u'object', u'script'],
                         value_type=TextLine(),
                         required=False)
    stripped_tags = List(title=_(u'Stripped tags'),
                         description=_(u'''These tags are stripped when saving or rendering,
                             but any content is preserved.'''),
                         default=[u'font', ],
                         value_type=TextLine(),
                         required=False)
    custom_tags = List(title=_(u'Custom tags'),
                         description=_(u'''Add tag names here for tags which are not part of HTML
                             but which should be permitted.'''),
                         default=[],
                         value_type=TextLine(),
                         required=False)


class IFilterAttributesSchema(Interface):
    stripped_attributes = List(title=_(u'Stripped attributes'),
                         description=_(u'''These attributes are stripped from any tag when saving.'''),
                         default=u'dir lang valign halign border frame rules cellspacing cellpadding bgcolor'.split(),
                         value_type=TextLine(),
                         required=False)
    
    stripped_combinations = Tuple(
                         title=_(u'Stripped combinations'),
                         description=_(u'''These attributes are stripped from any tag when saving.'''),
                         default=tuple(),
                         #default=u'dir lang valign halign border frame rules cellspacing cellpadding bgcolor'.split()
                         value_type=TextLine(), # XXX Needs to be a 2-tuple of lists of strings
                         required=False)
    
class IFilterEditorSchema(Interface):
    style_whitelist = List(title=_(u'Permitted styles'),
                         description=_(u'''These CSS styles are allowed in style attributes.'''),
                         default=u'text-align list-style-type float'.split(),
                         value_type=TextLine(),
                         required=False)

    class_whitelist = List(title=_(u'Permitted classes'),
                         description=_(u'''These class names styles are allowed
                             in class attributes. Any classes explicitly defined
                             within editor styles are also permitted.'''),
                         default=[],
                         value_type=TextLine(),
                         required=False)



class IFilterSchema(IFilterTagsSchema, IFilterAttributesSchema, IFilterEditorSchema):
    """Combined schema for the adapter lookup.
    """


class FilterControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(IFilterSchema)

    def __init__(self, context):
        super(FilterControlPanelAdapter, self).__init__(context)
        self.context = getToolByName(context, 'MailHost')
        pprop = getToolByName(context, 'portal_properties')
        self.site_properties = pprop.site_properties

    nasty_tags = ProxyFieldProperty(IFilterTagsSchema['nasty_tags'])
    stripped_tags = ProxyFieldProperty(IFilterTagsSchema['stripped_tags'])
    custom_tags = ProxyFieldProperty(IFilterTagsSchema['custom_tags'])
    style_whitelist = ProxyFieldProperty(IFilterEditorSchema['style_whitelist'])
    class_whitelist = ProxyFieldProperty(IFilterEditorSchema['class_whitelist'])
    stripped_attributes = ProxyFieldProperty(IFilterAttributesSchema['stripped_attributes'])
    stripped_combinations = ProxyFieldProperty(IFilterAttributesSchema['stripped_combinations'])


filtertagset = FormFieldsets(IFilterTagsSchema)
filtertagset.id = 'filtertags'
filtertagset.label = _(u'Tags')

filterattributes = FormFieldsets(IFilterAttributesSchema)
filterattributes.id = 'filterattributes'
filterattributes.label = _(u'Attributes')

filtereditor = FormFieldsets(IFilterEditorSchema)
filtereditor.id = 'filtereditor'
filtereditor.label = _(u'Styles')


class FilterControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(filtertagset, filterattributes, filtereditor)

    label = _("Html Filter settings")
    description = _("Html filtering settings for this site.")
    form_name = _("Html Filter Details")
