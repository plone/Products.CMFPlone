#this should be automated in the CMFSetup product
#you should be able to define Product dependencies and error messages
#in the config file

import zLOG

def log(message,summary='',severity=zLOG.ERROR):
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
    log("ExternalEditor not found.  If you want the external edit functionality, please download it from http://www.zope.org/Members/Caseman/ExternalEditor")

try:
    import Products.Epoz
except ImportError:
    log("Epoz not found.  It is strongly recommended if you want WYSIWYG capabilities in Plone. You can download it from http://www.zope.org/Members/mjablonski/Epoz/")


try:
    import Products.GroupUserFolder
except ImportError:
    log("GroupUserFolder not found. Please download it from http://sf.net/projects/collective")

