#this should be automated in the CMFSetup product
#you should be able to define Product dependencies and error messages
#in the config file

import zLOG

def log(message,summary='',severity=0):
    zLOG.LOG('Plone Dependency: ',severity,summary,message)

try:
    import Products.CMFQuickInstallerTool
except ImportError:
    log("CMFQuickInstallerTool not found.  Please download it from http://sf.net/projects/collective")

try:
    import Products.CMFActionIcons
except ImportError:
    log("CMFActionIcons not found.  Please download it from http://cvs.zope.org/Products/")

try:
    import Products.ExternalEditor
except ImportError:
    log("ExternalEditor not found.  Please download it from http://www.zope.org/Members/Caseman/ExternalEditor")

