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
    log("ExternalEditor not found.  If you want the external edit functionality, please download it from http://www.zope.org/Members/Caseman/ExternalEditor", severity=zLOG.INFO)

try:
    import Products.Epoz
except ImportError:
    log("Epoz not found.  If you want WYSIWYG capabilities in Plone, you can download it from http://www.zope.org/Members/mjablonski/Epoz/", severity=zLOG.INFO)


try:
    import Products.GroupUserFolder
except ImportError:
    log("GroupUserFolder not found. Please download it from http://sf.net/projects/collective")

