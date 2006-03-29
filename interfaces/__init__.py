# interface definitions for use by Plone

from properties import IPropertiesTool
from properties import ISimpleItemWithProperties
from basetool import IPloneBaseTool
from controlpanel import IControlPanel
from custpolicy import ICustomizationPolicy
from interface import IInterfaceTool
from siteroot import IPloneSiteRoot

import PropertiesTool
import PloneBaseTool
import PloneControlPanel
import CustomizationPolicy
import InterfaceTool

from Interface.bridge import createZope3Bridge
createZope3Bridge(IPropertiesTool, PropertiesTool, 'IPropertiesTool')
createZope3Bridge(ISimpleItemWithProperties, PropertiesTool,
                  'ISimpleItemWithProperties')
createZope3Bridge(IPloneBaseTool, PloneBaseTool, 'IPloneBaseTool')
createZope3Bridge(IControlPanel, PloneControlPanel, 'IControlPanel')
createZope3Bridge(ICustomizationPolicy, CustomizationPolicy,
                  'ICustomizationPolicy')
createZope3Bridge(IInterfaceTool, InterfaceTool, 'IInterfaceTool')
# BBB attach IPloneBaseTool to InterfaceTool module to make the
#     'testAvailableInterfaces' test pass
createZope3Bridge(IPloneBaseTool, InterfaceTool, 'IPloneBaseTool')
