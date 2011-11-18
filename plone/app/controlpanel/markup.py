from plone.fieldsets.fieldsets import FormFieldsets

from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.schema import Choice
from zope.schema import Tuple

from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import AllowedTypesWidget
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget

# For Archetypes markup

from Products.Archetypes.mimetype_utils import getDefaultContentType, \
    setDefaultContentType, getAllowedContentTypes, getAllowableContentTypes, \
    setForbiddenContentTypes

# For Wicked

from persistent import Persistent
from zope.annotation.interfaces import IAnnotations

try:
    from wicked.plone.registration import basic_type_regs as wicked_basic_type_regs
    from wicked.txtfilter import BrackettedWickedFilter
except ImportError:
    HAS_WICKED = False
else:
    HAS_WICKED = True

WICKED_SETTING_KEY="plone.app.controlpanel.wicked"

class WickedSettings(Persistent):
    """Settings for Wicked markup
    """
    types_enabled = []
    enable_mediawiki = False

if HAS_WICKED:
    wicked_type_regs = dict((factory.type, factory) for factory in \
                            wicked_basic_type_regs)

class WickedTypesVocabulary(object):
    """Vocabulary factory for wickedized portal types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        ttool = getToolByName(context, 'portal_types')
        items = []
        # Pretty insane code, but wicked uses different internal names for
        # the types :(
        for t in ttool.listContentTypes():
            for reg in wicked_basic_type_regs:
                if reg.type_id == t:
                    items.append(SimpleTerm(reg.type, reg.type, ttool[t].Title()))
        return SimpleVocabulary(items)

WickedTypesVocabularyFactory = WickedTypesVocabulary()

#
# Archetypes markup types
#

class ITextMarkupSchema(Interface):

    default_type = Choice(title=_(u'Default format'),
        description=_(u"Select the default format of textfields for newly "
                       "created content objects."),
        default=u'text/html',
        missing_value=set(),
        vocabulary="plone.app.vocabularies.AllowableContentTypes",
        required=True)

    allowed_types = Tuple(title=_(u'Alternative formats'),
        description=_(u"Select which formats are available for users as "
                       "alternative to the default format. Note that if new "
                       "formats are installed, they will be enabled for text "
                       "fields by default unless explicitly turned off here "
                       "or by the relevant installer."),
        required=True,
        missing_value=set(),
        value_type=Choice(
            vocabulary="plone.app.vocabularies.AllowableContentTypes"))

#
# Wicked behaviour
#

class IWikiMarkupSchema(Interface):

    wiki_enabled_types = Tuple(title=_(u"Choose which types will have wiki "
                                        "behavior."),
                               description=_(u"Each type chosen will have a "
                                             "wiki enabled primary text area. "
                                             "At least one type must be chosen "
                                             "to turn wiki behavior on."),
                               required=False,
                               missing_value=tuple(),
                               value_type=Choice(vocabulary="plone.app.\
controlpanel.WickedPortalTypes"))

#
# Combined schemata and fieldsets
#

if HAS_WICKED:
    class IMarkupSchema(ITextMarkupSchema, IWikiMarkupSchema):
        """Combined schema for the adapter lookup.
        """
else:
    IMarkupSchema = ITextMarkupSchema

class MarkupControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IMarkupSchema)

    def __init__(self, context):
        super(MarkupControlPanelAdapter, self).__init__(context)
        self.context = context
        self.toggle_mediawiki = False

    # Text markup settings

    def get_default_type(self):
        return getDefaultContentType(self.context)

    def set_default_type(self, value):
        setDefaultContentType(self.context, value)

    default_type = property(get_default_type, set_default_type)

    def get_allowed_types(self):
        return getAllowedContentTypes(self.context)

    def set_allowed_types(self, value):
        # The menu pretends to be a whitelist, but we are storing a blacklist
        # so that new types are available by default. So, we inverse the list.
        allowable_types = getAllowableContentTypes(self.context)
        forbidden_types = [t for t in allowable_types if t not in value]
        setForbiddenContentTypes(self.context, forbidden_types)

    allowed_types = property(get_allowed_types, set_allowed_types)

    # Wiki settings

    if HAS_WICKED:
        def get_enable_mediawiki(self):
            return self.wicked_settings.enable_mediawiki

        def set_enable_mediawiki(self, value):
            settings = self.wicked_settings
            if settings.enable_mediawiki != value:
                self.toggle_mediawiki = True
                settings.enable_mediawiki = value

        enable_mediawiki = property(get_enable_mediawiki, set_enable_mediawiki)

        def get_wiki_enabled_types(self):
            return self.wicked_settings.types_enabled

        def set_wiki_enabled_types(self, value):
            settings = self.wicked_settings
            if not self.toggle_mediawiki and value == settings.types_enabled:
                return

            self.unregister_wicked_types() # @@ use sets to avoid thrashing
            for name in value:
                reg = wicked_type_regs[name](self.context)
                if self.enable_mediawiki:
                    reg.txtfilter = BrackettedWickedFilter
                reg.handle()

            self.toggle_mediawiki = False
            settings.types_enabled = value

        wiki_enabled_types = property(get_wiki_enabled_types,
                                      set_wiki_enabled_types)

        @property
        def wicked_settings(self):
            ann = IAnnotations(self.context)
            return ann.setdefault(WICKED_SETTING_KEY, WickedSettings())

        def unregister_wicked_types(self):
            """Unregisters all previous registration objects
            """
            for name in wicked_type_regs.keys():
                wicked_type_regs[name](self.context).handle(unregister=True)

textset = FormFieldsets(ITextMarkupSchema)
textset.id = 'textmarkup'
textset.label = _(u'Text markup')

if HAS_WICKED:
    wikiset = FormFieldsets(IWikiMarkupSchema)
    wikiset.id = 'wiki'
    wikiset.label = _(u'Wiki behavior')

class MarkupControlPanel(ControlPanelForm):

    if HAS_WICKED:
        form_fields = FormFieldsets(textset, wikiset)
        form_fields['wiki_enabled_types'].custom_widget = MultiCheckBoxVocabularyWidget
    else:
        form_fields = FormFieldsets(textset)
    form_fields['allowed_types'].custom_widget = AllowedTypesWidget

    label = _("Markup settings")
    description = _("Lets you control what markup is available when editing "
                    "content.")
    form_name = _("Markup settings")
