# interface definitions for use by Plone

from properties import IPropertiesTool
from properties import ISimpleItemWithProperties
from basetool import IPloneBaseTool
from controlpanel import IControlPanel

import PropertiesTool
import PloneBaseTool
import PloneControlPanel

from Interface.bridge import createZope3Bridge
createZope3Bridge(IPropertiesTool, PropertiesTool, 'IPropertiesTool')
createZope3Bridge(ISimpleItemWithProperties, PropertiesTool,
                  'ISimpleItemWithProperties')
createZope3Bridge(IPloneBaseTool, PloneBaseTool, 'IPloneBaseTool')
createZope3Bridge(IControlPanel, PloneControlPanel, 'IControlPanel')
