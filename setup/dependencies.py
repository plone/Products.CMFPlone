#this should be automated in the CMFSetup product
#you should be able to define Product dependencies and error messages
#in the config file

import zLOG

def log(message,summary='',severity=zLOG.ERROR, optional=None):
    if optional:
        msg = 'Plone Option'
    else:
        msg = 'Plone Dependency'
    zLOG.LOG(msg,severity,summary,message)

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
    log("ExternalEditor not found.  If you want the external edit functionality, please download it from http://www.zope.org/Members/Caseman/ExternalEditor", severity=zLOG.INFO, optional=1)

try:
    import Products.Epoz
except ImportError:
    log("Epoz not found.  If you want WYSIWYG capabilities in Plone, you can download it from http://www.zope.org/Members/mjablonski/Epoz/", severity=zLOG.INFO, optional=1)


try:
    import Products.GroupUserFolder
except ImportError:
    log("GroupUserFolder not found. Please download it from http://sf.net/projects/collective", optional=1)

try:
    import Products.CMFFormControllerPatch
except ImportError:
    log("CMFFormControllerPatch not found. This is required for using Call Profiler with Plone, you can download it from http://sf.net/projects/collective", optional=1)

try:
    import Products.BTreeFolder2
except ImportError:
    log("BTreeFolder2 not found. Please download it from http://cvs.zope.org/Products")

try:
    import Products.Formulator
except ImportError:
    log("Formulator not found. Please download it from http://sourceforge.net/projects/formulator")
