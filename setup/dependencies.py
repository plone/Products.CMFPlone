#this should be automated in the CMFSetup product
#you should be able to define Product dependencies and error messages
#in the config file

import zLOG

def log(message,summary='',severity=zLOG.ERROR, optional=None):
    if optional:
        msg = 'Plone Option'
    else:
        msg = 'Plone Dependency'
    zLOG.LOG(msg,severity,summary,message + "\n")

# make sure CMF is installed
cmfcore = 0
try:
    import Products.CMFCore
    cmfcore = 1
except ImportError:
    log(("CMFCore not found.  Please download the CMF "
         "from http://cmf.zope.org/download"))

# check the CMF version
if cmfcore:
    from Products.CMFCore import cmfcore_globals
    from App.Common import package_home
    from os.path import join

    x = []
    CMF_VERSION = 'Unknown'
    try:
        file = join(package_home(cmfcore_globals), 'version.txt')
        CMF_VERSION = open(file, 'r').read().strip()
        version = CMF_VERSION
        filtered = ''
        for v in version:
            if v in ['0','1','2','3','4','5','6','7','8','9','.']:
                filtered += v
            else:
                break
        x = [int(x) for x in filtered.split('.')]
    except IOError:
        # couldnt find file, oh well
        pass
    except ValueError:
        # couldnt make sense of the version number
        pass
    if x < [1,4,2]:
        log(("Plone requires CMF 1.4.2 or later. "
             "Your version is: %s" % CMF_VERSION))

try:
    import Products.CMFQuickInstallerTool
except ImportError:
    log(("CMFQuickInstallerTool not found. "
         "Please download it from http://sf.net/projects/collective"))

try:
    import Products.CMFActionIcons
except ImportError:
    log(("CMFActionIcons not found. "
         "Please download it from http://cvs.zope.org/Products/"))

try:
    import Products.ExternalEditor
except ImportError:
    log(("ExternalEditor not found.  If you want "
         "the external edit functionality, please "
         "download it from "
         "http://www.zope.org/Members/Caseman/ExternalEditor"),
        severity=zLOG.INFO, optional=1)

try:
    import Products.Epoz
except ImportError:
    log(("Epoz not found.  If you want WYSIWYG capabilities "
        "in Plone, you can download it from "
        "http://www.zope.org/Members/mjablonski/Epoz/"),
        severity=zLOG.INFO, optional=1)

try:
    import Products.PlacelessTranslationService
except ImportError:
    log(("Placeless Translation Service not found. Plone "
         "runs without this, but if you want multilingual "
         "interface or access keys, you must download it from "
         "http://www.sourceforge.net/projects/collective"),
        severity=zLOG.INFO, optional=1)

try:
    import Products.CMFFormController
except ImportError:
    log(("CMFFormController not found. Please "
         "download if from http://sf.net/projects/collective"))

try:
    import Products.GroupUserFolder
except ImportError:
    log(("GroupUserFolder not found. Please "
         "download it from http://sf.net/projects/collective"))

try:
    import Products.CallProfiler
    try:
        import Products.CMFFormControllerPatch
    except ImportError:
        log(("CMFFormControllerPatch not found. This is "
             "only required for using Call Profiler with Plone, "
             "you can download it from "
             "http://sf.net/projects/collective"),
            severity=zLOG.INFO, optional=1)
except ImportError:
    pass

try:
    import Products.BTreeFolder2
except ImportError:
    log(("BTreeFolder2 not found. Please download it "
         "from http://cvs.zope.org/Products"))

try:
    import Products.Formulator
except ImportError:
    log(("Formulator not found. Please download it "
         "from http://sourceforge.net/projects/formulator"))
