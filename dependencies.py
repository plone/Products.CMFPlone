#this should be automated in the CMFSetup product
#you should be able to define Product dependencies and error messages
#in the config file

import zLOG

def log(message,summary='',severity=0):
    zLOG.LOG('Plone Depeedency: ',severity,summary,message)

try:
    import Products.CMFQuickInstallerTool
except ImportError:
    log("CMFQuickInstallerTool not found.  Please download it from sf.net/projects/collective.")

try:
    import Products.CMFActionIcons
except ImportError:
    log("CMFActionIcons not found.  Please download it from cvs.zope.org/CMF.")

try:
    import Products.ExternalEditor
except ImportError:
    log("ExternalEditor not found.  Please down it from http://www.zope.org/Members/Caseman/ExternalEditor")

