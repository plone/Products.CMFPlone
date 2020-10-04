# flake8: noqa
from Products.CMFPlone.interfaces.basetool import IPloneBaseTool
from Products.CMFPlone.interfaces.basetool import IPloneCatalogTool
from Products.CMFPlone.interfaces.basetool import IPloneTool
from Products.CMFPlone.interfaces.breadcrumbs import IHideFromBreadcrumbs
from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.CMFPlone.interfaces.controlpanel import IActionSchema
from Products.CMFPlone.interfaces.controlpanel import IControlPanel
from Products.CMFPlone.interfaces.controlpanel import IDateAndTimeSchema
from Products.CMFPlone.interfaces.controlpanel import IEditingSchema
from Products.CMFPlone.interfaces.controlpanel import IFilterSchema
from Products.CMFPlone.interfaces.controlpanel import IImagingSchema
from Products.CMFPlone.interfaces.controlpanel import ILinkSchema
from Products.CMFPlone.interfaces.controlpanel import ILoginSchema
from Products.CMFPlone.interfaces.controlpanel import IMailSchema
from Products.CMFPlone.interfaces.controlpanel import IMaintenanceSchema
from Products.CMFPlone.interfaces.controlpanel import IMarkupSchema
from Products.CMFPlone.interfaces.controlpanel import INavigationSchema
from Products.CMFPlone.interfaces.controlpanel import INewActionSchema
from Products.CMFPlone.interfaces.controlpanel import ISearchSchema
from Products.CMFPlone.interfaces.controlpanel import ISecuritySchema
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.CMFPlone.interfaces.controlpanel import ISocialMediaSchema
from Products.CMFPlone.interfaces.controlpanel import ITinyMCEAdvancedSchema
from Products.CMFPlone.interfaces.controlpanel import ITinyMCELayoutSchema
from Products.CMFPlone.interfaces.controlpanel import ITinyMCEPluginSchema
from Products.CMFPlone.interfaces.controlpanel import ITinyMCEResourceTypesSchema
from Products.CMFPlone.interfaces.controlpanel import ITinyMCESchema
from Products.CMFPlone.interfaces.controlpanel import ITinyMCESpellCheckerSchema
from Products.CMFPlone.interfaces.controlpanel import ITypesSchema
from Products.CMFPlone.interfaces.controlpanel import IUserGroupsSettingsSchema
from Products.CMFPlone.interfaces.events import IConfigurationChangedEvent
from Products.CMFPlone.interfaces.events import IReorderedEvent
from Products.CMFPlone.interfaces.events import ISiteManagerCreatedEvent
from Products.CMFPlone.interfaces.installable import INonInstallable
from Products.CMFPlone.interfaces.interface import IInterfaceTool
from Products.CMFPlone.interfaces.language import ILanguage
from Products.CMFPlone.interfaces.login import IForcePasswordChange
from Products.CMFPlone.interfaces.login import IInitialLogin
from Products.CMFPlone.interfaces.login import ILogin
from Products.CMFPlone.interfaces.login import ILoginForm
from Products.CMFPlone.interfaces.login import ILoginFormSchema
from Products.CMFPlone.interfaces.login import ILoginHelpForm
from Products.CMFPlone.interfaces.login import ILoginHelpFormSchema
from Products.CMFPlone.interfaces.login import IRedirectAfterLogin
from Products.CMFPlone.interfaces.migration import IMigrationTool
from Products.CMFPlone.interfaces.password_reset import IPasswordResetToolView
from Products.CMFPlone.interfaces.password_reset import IPWResetTool
from Products.CMFPlone.interfaces.patterns import IPatternsSettings
from Products.CMFPlone.interfaces.properties import IPropertiesTool
from Products.CMFPlone.interfaces.properties import ISimpleItemWithProperties
from Products.CMFPlone.interfaces.resources import IBundleRegistry
from Products.CMFPlone.interfaces.resources import IResourceRegistry
from Products.CMFPlone.interfaces.siteroot import IMigratingPloneSiteRoot
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.interfaces.siteroot import ITestCasePloneSiteRoot
from Products.CMFPlone.interfaces.structure import INonStructuralFolder
from Products.CMFPlone.interfaces.syndication import ISiteSyndicationSettings
from Products.CMFPlone.interfaces.translationservice import ITranslationServiceTool
from Products.CMFPlone.interfaces.workflow import IWorkflowChain

from zope.deferredimport import deprecated


deprecated(
    "It has been moved to plone.i18n.interfaces, import from there instead.",
    ILanguageSchema='plone.i18n.interfaces:ILanguageSchema',
)
