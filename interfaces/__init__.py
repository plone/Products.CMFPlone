# interface definitions for use by Plone

from properties import IPropertiesTool
from properties import ISimpleItemWithProperties
from basetool import IPloneBaseTool
from controlpanel import IControlPanel
from interface import IInterfaceTool
from migration import IMigrationTool
from siteroot import IPloneSiteRoot
from constrains import IConstrainTypes
from constrains import ISelectableConstrainTypes
from structure import INonStructuralFolder
from view import IBrowserDefault
from view import ISelectableBrowserDefault
from view import IDynamicViewTypeInformation
from factory import IFactoryTool
from translationservice import ITranslationServiceTool

import PropertiesTool
import PloneBaseTool
import PloneControlPanel
import InterfaceTool
import ConstrainTypes
import NonStructuralFolder

from Interface.bridge import createZope3Bridge

createZope3Bridge(IPropertiesTool, PropertiesTool, 'IPropertiesTool')
createZope3Bridge(ISimpleItemWithProperties, PropertiesTool, 'ISimpleItemWithProperties')
createZope3Bridge(IPloneBaseTool, PloneBaseTool, 'IPloneBaseTool')
createZope3Bridge(IControlPanel, PloneControlPanel, 'IControlPanel')
createZope3Bridge(IInterfaceTool, InterfaceTool, 'IInterfaceTool')
createZope3Bridge(IConstrainTypes, ConstrainTypes, 'IConstrainTypes')
createZope3Bridge(ISelectableConstrainTypes, ConstrainTypes, 'ISelectableConstrainTypes')
createZope3Bridge(INonStructuralFolder, NonStructuralFolder, 'INonStructuralFolder')

# BBB attach IPloneBaseTool to InterfaceTool module to make the
#     'testAvailableInterfaces' test pass
createZope3Bridge(IPloneBaseTool, InterfaceTool, 'IPloneBaseTool')
