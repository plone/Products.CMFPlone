from Acquisition import aq_base
from plone.fieldsets.fieldsets import FormFieldsets
from zope.interface import Interface, implements
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import implements
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import List
from zope.schema import Tuple
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import BrowserView

from plone.app.vocabularies.types import BAD_TYPES

from form import ControlPanelForm
from widgets import MultiCheckBoxThreeColumnWidget as MCBThreeColumnWidget
from widgets import MultiCheckBoxVocabularyWidget


anon_auth_items = (('anon', _(u'anonymous users')),
                   ('auth', _(u'logged in users'),))

anon_auth_terms = [SimpleTerm(item[0], title=item[1]) for item in
                   anon_auth_items]

AnonAuthVocabulary = SimpleVocabulary(anon_auth_terms)

class IBaseSearchSchema(Interface):

    enable_livesearch = Bool(
        title=_(u'Enable LiveSearch'),
        description=_(u"Enables the LiveSearch feature, which shows live "
                       "results if the browser supports JavaScript."),
        default=False,
        required=True
        )

    types_not_searched = Tuple(
        title=_(u"Define the types to be shown in the site and searched"),
        description=_(u"Define the types that should be searched and be "
                       "available in the user facing part of the site. "
                       "Note that if new content types are installed, they "
                       "will be enabled by default unless explicitly turned "
                       "off here or by the relevant installer."),
        required=True,
        missing_value=tuple(),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes")
        )


class IAdvancedSearchSchema(Interface):

    search_review_state_for_anon = Bool(
        title=_(u'Show review states to visitors that are not logged in'),
        description=_(u"Visitors to your site mostly don't know what review"
                       "states are. By default we display the option to "
                       "search by review state to logged in users only. "
                       "You can enable this option let anonymous Visitors "
                       "search by review state also."),
        required=True,
        default=False
        )

    search_enable_sort_on = List(
        title=_(u"Sort order of search results"),
        description=_(u"If enabled, the user can select if he wants to "
                      u"sort the results by relevance, title, creation or "
                      u"modification date"),
        value_type=Choice(vocabulary=AnonAuthVocabulary),
        required=False,
        )

    search_enable_batch_size = List(
        title=_(u"Search results per page"),
        description=_(u"If enabled, the user can choose if he "
                      u"wants to see 30, 60 or 90 results per page. If "
                      u"disabled, he will see 30 results per page."),
        value_type=Choice(vocabulary=AnonAuthVocabulary),
        required=False,
        )

    search_enable_title_search = List(
        title=_(u"Search in the title only"),
        description=_(u"If enabled, the form contains a field to search in "
                      u"the title only. Note that the form already contains "
                      u"a field to search all text."),
        value_type=Choice(vocabulary=AnonAuthVocabulary),
        required=False,
        )

    search_enable_description_search = List(
        title=_(u"Search in the description only"),
        description=_(u"If enabled, the form contains a field to search "
                      u"in the description only. Note that the form already "
                      u"contains a field to search all text."),
        value_type=Choice(vocabulary=AnonAuthVocabulary),
        required=False,
        )

    search_collapse_options = Bool(
        title=_(u"Collapse rarely used options"),
        description=_(u"If enabled, the rarely used search options, e.g. for "
                      "the workflow state are collapsed by default and only "
                      "the label of the search option is visible. If the user "
                      "clicks on the label of the search option, the option is "
                      u"expanded."),
        default=True,
        required=False,
        )


class ISearchSchema(IBaseSearchSchema, IAdvancedSearchSchema):
    ''' Both base and advanced search form options '''


class ISearchFormOptions(Interface):

    def collapse():
        '''collapse items'''

    def show_description():
        '''show search options for the description'''

    def show_title():
        '''show option to search in the title only'''

    def show_sort_on():
        '''show option to choose sort_on'''

    def show_batch_size():
        '''show option to choose the batch size'''

    def show_review_state():
        '''show option to search by review state'''


class SearchFormOptions(BrowserView):
    implements(ISearchFormOptions)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        portal = getToolByName(context, 'portal_url').getPortalObject()
        self.is_anonymous = getToolByName(context,
                                          'portal_membership').isAnonymousUser()
        self.properties = ISearchSchema(portal)

    def test_show(self, values):
        if self.is_anonymous:
            return 'anon' in values
        else:
            return 'auth' in values

    def collapse(self):
        return self.properties.search_collapse_options

    def show_description(self):
        return self.test_show(self.properties.search_enable_description_search)

    def show_title(self):
        return self.test_show(self.properties.search_enable_title_search)

    def show_sort_on(self):
        return self.test_show(self.properties.search_enable_sort_on)

    def show_batch_size(self):
        return self.test_show(self.properties.search_enable_batch_size)

    def show_review_state(self):
        if self.is_anonymous:
            return self.properties.search_review_state_for_anon
        else:
            return True


class SearchControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(ISearchSchema)

    def __init__(self, context):
        super(SearchControlPanelAdapter, self).__init__(context)
        pprop = getToolByName(context, 'portal_properties')
        self.context = pprop.site_properties
        self.jstool = getToolByName(context, 'portal_javascripts')
        self.ttool = getToolByName(context, 'portal_types')

    def get_enable_livesearch(self):
        return self.context.enable_livesearch

    def set_enable_livesearch(self, value):
        if value:
            self.context.manage_changeProperties(enable_livesearch=True)
            self.jstool.getResource('livesearch.js').setEnabled(True)
        else:
            self.context.manage_changeProperties(enable_livesearch=False)
            self.jstool.getResource('livesearch.js').setEnabled(False)
        self.jstool.cookResources()

    enable_livesearch = property(get_enable_livesearch, set_enable_livesearch)

    def get_types_not_searched(self):
        # Note: we do not show BAD_TYPES.
        return [t for t in self.ttool.listContentTypes()
                        if t not in self.context.types_not_searched and
                           t not in BAD_TYPES]

    def set_types_not_searched(self, value):
        # Note: we add BAD_TYPES to the value list.
        value = [t for t in self.ttool.listContentTypes() if t not in value
                   or t in BAD_TYPES]
        self.context._updateProperty('types_not_searched', value)

    # This also defines the user friendly types
    types_not_searched = property(get_types_not_searched,
                                  set_types_not_searched)

    def get_search_collapse_options(self):
        return self.context.search_collapse_options

    def set_search_collapse_options(self, value):
        self.context._updateProperty('search_collapse_options', value)

    search_collapse_options = property(get_search_collapse_options,
                                       set_search_collapse_options)

    def get_search_enable_description_search(self):
        return self.context.search_enable_description_search

    def set_search_enable_description_search(self, value):
        self.context._updateProperty('search_enable_description_search', value)

    search_enable_description_search = property(
        get_search_enable_description_search,
        set_search_enable_description_search)

    def get_search_enable_title_search(self):
        return self.context.search_enable_title_search

    def set_search_enable_title_search(self, value):
        self.context._updateProperty('search_enable_title_search', value)

    search_enable_title_search = property(get_search_enable_title_search,
                                          set_search_enable_title_search)

    def get_search_enable_batch_size(self):
        return self.context.search_enable_batch_size

    def set_search_enable_batch_size(self, value):
        self.context._updateProperty('search_enable_batch_size', value)

    search_enable_batch_size = property(get_search_enable_batch_size,
                                        set_search_enable_batch_size)

    def get_search_enable_sort_on(self):
        return self.context.search_enable_sort_on

    def set_search_enable_sort_on(self, value):
        self.context._updateProperty('search_enable_sort_on', value)

    search_enable_sort_on = property(get_search_enable_sort_on,
                                        set_search_enable_sort_on)

    def get_search_review_state_for_anon(self):
        return self.context.search_review_state_for_anon

    def set_search_review_state_for_anon(self, value):
        self.context._updateProperty('search_review_state_for_anon', value)

    search_review_state_for_anon = property(get_search_review_state_for_anon,
                                            set_search_review_state_for_anon)


searchset = FormFieldsets(IBaseSearchSchema)
searchset.id = 'search'
searchset.label = _("Search settings")

advancedset = FormFieldsets(IAdvancedSearchSchema)
advancedset.id = 'advanced'
advancedset.label = _("Advanced search form settings")
advancedset.description = _("Configure when and how to show search options in the advanced search form.")

class SearchControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(searchset, advancedset)
    form_fields['types_not_searched'].custom_widget = MCBThreeColumnWidget
    form_fields['types_not_searched'].custom_widget.cssClass='label'

    for fieldname in ['search_enable_description_search',
                      'search_enable_title_search',
                      'search_enable_batch_size',
                      'search_enable_sort_on']:
        form_fields[fieldname].custom_widget = MultiCheckBoxVocabularyWidget
        form_fields[fieldname].custom_widget.cssClass='label'

    label = _("Search settings")
    description = _("Search settings for this site.")
    form_name = _("Search settings")
