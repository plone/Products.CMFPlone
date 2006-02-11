# interface definitions for use by Plone

from properties import *

import PropertiesTool

from Interface.bridge import createZope3Bridge
createZope3Bridge(IPropertiesTool, PropertiesTool, 'IPropertiesTool')
