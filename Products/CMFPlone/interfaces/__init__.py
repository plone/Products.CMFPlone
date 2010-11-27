# interface definitions

from properties import IPropertiesTool
from properties import ISimpleItemWithProperties
from basetool import IPloneBaseTool
from basetool import IPloneTool
from basetool import IPloneCatalogTool
from controlpanel import IControlPanel
from events import ISiteManagerCreatedEvent
from interface import IInterfaceTool
from installable import INonInstallable
from migration import IMigrationTool
from siteroot import IPloneSiteRoot
from siteroot import IMigratingPloneSiteRoot
from siteroot import ITestCasePloneSiteRoot
from constrains import IConstrainTypes
from constrains import ISelectableConstrainTypes
from structure import INonStructuralFolder
from factory import IFactoryTool
from translationservice import ITranslationServiceTool
from breadcrumbs import IHideFromBreadcrumbs
from workflow import IWorkflowChain

import zope.deferredimport

zope.deferredimport.deprecated(
    "It has been moved to Products.CMFDynamicViewFTI.interfaces. "
    "This alias will be removed in Plone 5.0",
    IBrowserDefault = 'Products.CMFDynamicViewFTI.interfaces:IBrowserDefault',
    )

zope.deferredimport.deprecated(
    "It has been moved to Products.CMFDynamicViewFTI.interfaces. "
    "This alias will be removed in Plone 5.0",
    IDynamicViewTypeInformation = 'Products.CMFDynamicViewFTI.interfaces:IDynamicViewTypeInformation',
    )

zope.deferredimport.deprecated(
    "It has been moved to Products.CMFDynamicViewFTI.interfaces. "
    "This alias will be removed in Plone 5.0",
    ISelectableBrowserDefault = 'Products.CMFDynamicViewFTI.interfaces:ISelectableBrowserDefault',
    )
