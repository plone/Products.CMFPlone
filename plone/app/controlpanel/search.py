from plone.fieldsets.fieldsets import FormFieldsets
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.schema import Bool
from zope.schema import Choice
from zope.schema import Tuple
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.vocabularies.types import BAD_TYPES

from form import ControlPanelForm
from widgets import MultiCheckBoxThreeColumnWidget as MCBThreeColumnWidget


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


class ISearchSchema(IBaseSearchSchema):
    ''' Base search form options '''


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


searchset = FormFieldsets(IBaseSearchSchema)
searchset.id = 'search'
searchset.label = _("Search settings")

class SearchControlPanel(ControlPanelForm):

    form_fields = FormFieldsets(searchset)
    form_fields['types_not_searched'].custom_widget = MCBThreeColumnWidget
    form_fields['types_not_searched'].custom_widget.cssClass='label'

    label = _("Search settings")
    description = _("Search settings for this site.")
    form_name = _("Search settings")
