from plone.fieldsets import FormFieldsets
from plone.fieldsets.form import FieldsetsEditForm

from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope import schema
from zope.formlib.form import action
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import ListSequenceWidget

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.formlib.formbase import PageForm

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.form import named_template_adapter
#from plone.app.controlpanel.form import ControlPanelForm

from Products.Five.formlib.formbase import PageForm

class IMinMaxRange(Interface):
    query = schema.List(title=u"query",
        value_type=schema.Int(),
        default=[0,10000000],
        min_length=2, max_length=2, required=False,
        )
    range = schema.TextLine(title=u"range", default=u"minmax")

class MinMaxRange:
    implements(IMinMaxRange)
    def __init__(self, tags='', attributes=''):
        self.tags = tags
        self.attributes = attributes

class IDCSearchSchema(Interface):

    SearchableText = schema.TextLine(title=u'Search Text',
                           description=u'The text to search for',
                           required=False)

    Description = schema.TextLine(title=u'Description',
                           required=False)

class IMarsSearchSchema(Interface):

    BPdating = schema.Dict(title=u'BP Dating',
                           description=u'How many years before 1950.',
                           required=False)

class ISearchSchema(IDCSearchSchema, IMarsSearchSchema):
    """Concatenated fieldsets."""


class ISearchView(Interface):
    """Marker Interface."""


class SearchViewAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(ISearchSchema)

    def __init__(self, context):
        super(SearchViewAdapter, self).__init__(context)
        self.context = context
        self.request = context.request

    @apply
    def SearchableText():
        def get(self):
            return self.request.get('text', '')
        return property(get)

    @apply
    def Description():
        def get(self):
            return self.request.get('description', '')
        return property(get)

    @apply
    def BPdating():
        def get(self):
            return self.request.get('BPdating',
                                    {'query':[0,10000000], 'range': 'minmax'})
        return property(get)


searchdublincoreset = FormFieldsets(IDCSearchSchema)
searchdublincoreset.id = 'dublincore'
searchdublincoreset.label = _(u'label_dublincore', default=u'Dublin Core')

searchmarsset = FormFieldsets(IMarsSearchSchema)
searchmarsset.id = 'mars'
searchmarsset.label = _(u'label_mars', default=u'MARS')



class SearchView(FieldsetsEditForm):

    implements(ISearchView)

    form_fields = FormFieldsets(searchdublincoreset, searchmarsset)
#    form_fields['stripped_combinations'].custom_widget = combination_widget


    label = _("Search Form")
    description = _("MARS Advanced search form.")
    form_name = _("Search Form")


    @action("search")
    def action_search(self, action, data):
        catalog = getToolByName(self.context, 'portal_catalog')
    
        kwargs = {}
        if data['SearchableText']:
            kwargs['SearchableText'] = data['SearchableText']
        if data['Description']:
            kwargs['Description'] = data['Description']
    
        self.search_results = catalog(**kwargs)
        self.search_results_count = len(self.search_results)
        self.data = data
        return self.template()

_template = ViewPageTemplateFile('search.pt')
search_named_template_adapter = named_template_adapter(_template)
