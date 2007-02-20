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
from Products.PortalTransforms.transforms.safe_html import VALID_TAGS

from form import ControlPanelForm

XHTML_TAGS = set(
    'a abbr acronym address area b base bdo big blockquote body br '
    'button caption cite code col colgroup dd del div dfn dl dt em '
    'fieldset form h1 h2 h3 h4 h5 h6 head hr html i img input ins kbd '
    'label legend li link map meta noscript object ol optgroup option '
    'p param pre q samp script select small span strong style sub sup '
    'table tbody td textarea tfoot th thead title tr tt ul var'.split())


class IFilterTagsSchema(Interface):

    nasty_tags = List(
        title=_(u'Nasty tags'),
        description=_(u"These tags, and their content are completely blocked "
                      "when a page is save or rendered."),
        default=[u'applet', u'embed', u'object', u'script'],
        value_type=TextLine(),
        required=False)

    stripped_tags = List(
        title=_(u'Stripped tags'),
        description=_(u"These tags are stripped when saving or rendering,"
                      "but any content is preserved."),
        default=[u'font', ],
        value_type=TextLine(),
        required=False)

    
    custom_tags = List(
        title=_(u'Custom tags'),
        description=_(u"Add tag names here for tags which are not part of "
                      "XHTML but which should be permitted."),
        default=[],
        value_type=TextLine(),
        required=False)


class IFilterAttributesSchema(Interface):
    stripped_attributes = List(
        title=_(u'Stripped attributes'),
        description=_(u"These attributes are stripped from any tag when "
                      "saving."),
        default=(u'dir lang valign halign border frame rules cellspacing '
                 'cellpadding bgcolor').split(),
        value_type=TextLine(),
        required=False)
    
    stripped_combinations = Tuple(
        title=_(u'Stripped combinations'),
        description=_(u"These attributes are stripped from any tag when "
                      "saving."),
        default=tuple(),
        #default=u'dir lang valign halign border frame rules cellspacing cellpadding bgcolor'.split()
        value_type=TextLine(), # XXX Needs to be a 2-tuple of lists of strings
        required=False)

class IFilterEditorSchema(Interface):
    style_whitelist = List(
        title=_(u'Permitted styles'),
        description=_(u'These CSS styles are allowed in style attributes.'),
        default=u'text-align list-style-type float'.split(),
        value_type=TextLine(),
        required=False)
    
    class_whitelist = List(
        title=_(u'Permitted classes'),
        description=_(u'These class names styles are allowed in class '
                      'attributes. Any classes explicitly defined '
                      'within editor styles are also permitted.'),
        default=[],
        value_type=TextLine(),
        required=False)


class IFilterSchema(IFilterTagsSchema, IFilterAttributesSchema,
                    IFilterEditorSchema):
    """Combined schema for the adapter lookup.
    """

class FilterControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(IFilterSchema)

    def __init__(self, context):
        super(FilterControlPanelAdapter, self).__init__(context)
        self.context = context
        self.transform = getattr(
            getToolByName(context, 'portal_transforms'), 'safe_html')
        self.kupu_tool = getToolByName(context, 'kupu_library_tool')

    def _settransform(self, **kwargs):
        # Cannot pass a dict to set transform parameters, it has
        # to be separate keys and values
        # Also the transform requires all dictionary values to be set
        # at the same time: other values may be present but are not
        # required.
        for k in ('valid_tags', 'nasty_tags'):
            if k not in kwargs:
                kwargs[k] = self.transform.get_parameter_value(k)

        for k in list(kwargs):
            if isinstance(kwargs[k], dict):
                v = kwargs[k]
                kwargs[k+'_key'] = v.keys()
                kwargs[k+'_value'] = [str(s) for s in v.values()]
                del kwargs[k]
        self.transform.set_parameters(**kwargs)
        self.transform._p_changed = True
        self.transform.reload()

    @apply
    def nasty_tags():
        def get(self):
            return sorted(self.transform.get_parameter_value('nasty_tags'))
        def set(self, value):
            value = dict.fromkeys(value, 1)
            valid = self.transform.get_parameter_value('valid_tags')
            for v in value:
                if v in valid:
                    del valid[v]
            self._settransform(nasty_tags=value, valid_tags=valid)
        return property(get, set)

    @apply
    def stripped_tags():
        def get(self):
            valid = set(self.transform.get_parameter_value('valid_tags'))
            stripped = XHTML_TAGS - valid
            return sorted(stripped)
        def set_(self, value):
            valid = dict(self.transform.get_parameter_value('valid_tags'))
            stripped = set(value)
            for v in XHTML_TAGS:
                if v in stripped:
                    if v in valid:
                        del valid[v]
                else:
                    valid[v] = VALID_TAGS.get(v, 1)

            # Nasty tags must never be valid
            for v in self.nasty_tags:
                if v in valid:
                    del valid[v]
            self._settransform(valid_tags=valid)
        return property(get, set_)

    @apply
    def custom_tags():
        def get(self):
            valid = set(self.transform.get_parameter_value('valid_tags'))
            custom = valid - XHTML_TAGS
            return sorted(custom)
        def set_(self, value):
            valid = dict(self.transform.get_parameter_value('valid_tags'))
            # Remove all non-standard tags
            for v in valid.keys():
                if v not in XHTML_TAGS:
                    del valid[v]
            # Now add in the custom tags
            for v in value:
                if v not in valid:
                    valid[v] = 1

            self._settransform(valid_tags=valid)

        return property(get, set_)


    @apply
    def style_whitelist():
        def get(self):
            return []
        def set(self, value):
            pass
        return property(get, set)

    @apply
    def class_whitelist():
        def get(self):
            return []
        def set(self, value):
            pass
        return property(get, set)

    @apply
    def stripped_attributes():
        def get(self):
            return []
        def set(self, value):
            pass
        return property(get, set)

    @apply
    def stripped_combinations():
        def get(self):
            return []
        def set(self, value):
            pass
        return property(get, set)


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

