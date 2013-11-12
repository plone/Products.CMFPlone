from zope.interface import Interface
from properties import IPropertiesTool
from properties import ISimpleItemWithProperties
from basetool import IPloneBaseTool
from basetool import IPloneTool
from basetool import IPloneCatalogTool
from controlpanel import IControlPanel
from events import ISiteManagerCreatedEvent
from events import IReorderedEvent
from interface import IInterfaceTool
from installable import INonInstallable
from migration import IMigrationTool
from siteroot import IPloneSiteRoot
from siteroot import IMigratingPloneSiteRoot
from siteroot import ITestCasePloneSiteRoot
from constrains import IConstrainTypes
from constrains import ISelectableConstrainTypes
from structure import INonStructuralFolder
from translationservice import ITranslationServiceTool
from breadcrumbs import IHideFromBreadcrumbs
from workflow import IWorkflowChain

import pkg_resources
try:
    pkg_resources.get_distribution('Products.ATContentTypes')
except pkg_resources.DistributionNotFound:
    class IFactoryTool(Interface):
        ''' Replacement for a needed interface
        '''
else:
    from Products.ATContentTypes.interfaces import IFactoryTool

IFactoryTool  # pyflakes
