from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_hasattr
from form import ControlPanelForm
from persistent import Persistent
from wicked.plone.registration import basic_type_regs
from wicked.txtfilter import BrackettedWickedFilter
from zope.annotation.interfaces import IAnnotations
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.component import adapts
from zope.formlib.form import FormFields
from zope.interface import Interface, implements
from zope.schema import Int, TextLine
from zope.schema import Tuple, Bool, Choice
from zope.schema.vocabulary import SimpleVocabulary

type_regs = dict((factory.type, factory) for factory in basic_type_regs)

def propify(func):
    return property(**func())

class IWickedSchema(Interface):

    types_enabled = Tuple(title=_(u'Choose which types will have wiki behavior.'),
                          description=_(u"""Each type chosen will have a wiki enabled primary text area. At least
                          one type must be chosen to turn wiki behavior on"""),
                          required=False,
                          missing_value=tuple(),
                          value_type=Choice(vocabulary="plone.app.controlpanel.WickedPortalTypes"))
    
    enable_mediawiki = Bool(title=_(u'Use Media wiki style syntax: [[my link]]'),
                            description=_(u"""Use brackets rather than the internationally usable default (( ))"""),
                            default=False)


SETTING_KEY="plone.app.controlpanel.wicked"


class WickedControlPanelAdapter(SchemaAdapterBase):    

    adapts(IPloneSiteRoot)
    implements(IWickedSchema)
    toggle_mediawiki = False
    
    def __init__(self, context):
        super(self.__class__, self).__init__(context)
        self.site = context
        self.context = self.settings

    @property
    def settings(self):
        ann = IAnnotations(self.site)
        settings = ann.get(SETTING_KEY)
        if not settings:
            ann[SETTING_KEY] = WickedSettings()
            settings = ann[SETTING_KEY]
        return settings

    def unregister(self):
        """unregisters all previous registration objects"""
        for name in type_regs.keys():
            type_regs[name](self.site).handle(unregister=True)


    @propify
    def enable_mediawiki():
        def fget(self):
            return self.settings.enable_mediawiki
        
        def fset(self, value):
            if value != self.enable_mediawiki:
                self.toggle_mediawiki = True
            self.settings.enable_mediawiki = value
        return locals()

    @propify
    def types_enabled():
        def fget(self):
            return self.settings.types_enabled
        
        def fset(self, value):
            if value == self.settings.types_enabled:
                return

            self.unregister() # @@ use sets to avoid thrashing
            for name in value:
                reg = type_regs[name](self.site)
                if self.enable_mediawiki:
                    reg.txtfilter = BrackettedWickedFilter
                reg.handle()
            self.toggle_mediawiki=False
            self.settings.types_enabled = value
        return locals()


class WickedSettings(Persistent):
    """setting bag"""
    types_enabled=[]
    enable_mediawiki=False

class WickedControlPanel(ControlPanelForm):
    form_fields = FormFields(IWickedSchema)
    label = _("Wiki (Wicked) settings")
    description = _("Select style of wiki behavior and what content types should act wiki-ish")
    form_name = label


class WickedTypesVocabulary(object):
    """Vocabulary factory for wickedized portal types.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        items = [(reg.type, reg.type) for key, reg in type_regs.items()]
        return SimpleVocabulary.fromItems(items)


WickedTypesVocabularyFactory = WickedTypesVocabulary()


def test_suite():
    from zope.testing import doctest
    from unittest import TestSuite

    from Testing.ZopeTestCase import FunctionalDocFileSuite
    from Products.PloneTestCase import ptc
    from Products.CMFCore.utils import getToolByName
    from tests.test_doctests import ControlPanelTestCase

    ptc.setupPloneSite()

    OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
                   doctest.ELLIPSIS |
                   doctest.NORMALIZE_WHITESPACE)

    docsuite = FunctionalDocFileSuite('wicked.txt',
                           optionflags=OPTIONFLAGS,
                           globs=globals(),
                           package="plone.app.controlpanel",
                           test_class=ControlPanelTestCase)
    return docsuite

tests = test_suite


