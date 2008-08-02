import logging
import sys

MINIMUM_PYTHON_VER = (2, 4, 3)
PREFERRED_PYTHON_VER = "2.4.4 or newer"

MINIMUM_ZOPE_VER = (2, 10, 4)
PREFERRED_ZOPE_VER = "2.10.4 or newer"

MINIMUM_CMF_VER = (2, 1, 0)

messages = []

def log(message, summary='', severity=logging.ERROR, optional=0):
    if optional:
        subsys = 'Plone Option'
    else:
        subsys = 'Plone Dependency'
    messages.append({'message' : message, 'summary' : summary,
                     'severity' : severity, 'optional' : optional
            })
    logger = logging.getLogger(subsys)
    logger.log(severity, '%s \n%s', summary, message)

# test python version
PYTHON_VER = sys.version_info[:3]
if PYTHON_VER < MINIMUM_PYTHON_VER:
    log(("Python version %s found but Plone needs at least "
         "Python %s. Please download and install Python %s "
     "from http://python.org/" % (PYTHON_VER,
     MINIMUM_PYTHON_VER, PREFERRED_PYTHON_VER) ))

# test zope version
ZOPE_VER = "unknown"
try:
    from App.version_txt import getZopeVersion
except ImportError:
    pass
else:
    try:
        ZOPE_VER = getZopeVersion()[:3]
    except (ValueError, TypeError, KeyError):
        pass

if ZOPE_VER in ('unknown', (-1, -1, -1)): # -1, -1, 1 is developer release
    log(("Unable to detect Zope version. Please make sure you have Zope "
         "%s installed." % PREFERRED_ZOPE_VER), severity=logging.INFO)
elif ZOPE_VER < MINIMUM_ZOPE_VER:
    log(("Zope version %s found but Plone needs at least "
         "Zope %s Please download and install Zope %s "
     "from http://zope.org/" %
     ('.'.join([str(x) for x in ZOPE_VER]),
       '.'.join([str(x) for x in MINIMUM_ZOPE_VER]), PREFERRED_ZOPE_VER) ))

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
    from Products.CMFCore.utils import _wwwdir
    from os.path import join

    x = []
    CMF_VERSION = 'Unknown'
    try:
        file = join(_wwwdir, '..', 'version.txt')
        CMF_VERSION = open(file, 'r').read().strip()
        version = CMF_VERSION.strip()
        if version.lower().startswith('cmf-'):
            version = version[4:]
        filtered = ''
        for v in version:
            if v in ['0','1','2','3','4','5','6','7','8','9','.']:
                filtered += v
            else:
                break
        cmf_ver = [int(x) for x in filtered.split('.')]

        if tuple(cmf_ver) < MINIMUM_CMF_VER:
            log(("Plone requires CMF %s or later. "
                 "Your version is: %s" % (MINIMUM_CMF_VER, CMF_VERSION)))
    except IOError:
        # couldnt find file, oh well
        pass
    except ValueError:
        # couldnt make sense of the version number
        pass

try:
    import Products.CMFQuickInstallerTool
except ImportError:
    log(("CMFQuickInstallerTool not found. Please download it from "
         "http://plone.org/products/cmfquickinstallertool"))

try:
    # TODO: we might want to check if the user has jpeg and zlib support, too
    import PIL.Image
except ImportError:
    log(("PIL not found. Plone needs PIL 1.1.5 or newer. "
         "Please download it from http://www.pythonware.com/products/pil/ or "
         "http://effbot.org/downloads/#Imaging"))

try:
    from elementtree import ElementTree
except ImportError:
    log(("Elementtree not found. Plone needs Elementtree for XML "
         "transformation. Please download it from "
         "http://effbot.org/downloads/#elementtree"),
         severity=logging.INFO)

try:
    import Products.ExternalEditor
except ImportError:
    log(("ExternalEditor not found. If you want "
         "the external edit functionality, please "
         "download it from "
         "http://plope.com/software/ExternalEditor"),
        severity=logging.INFO, optional=1)

try:
    import Products.kupu
except ImportError:
    log(("Kupu not found. If you want WYSIWYG capabilities "
        "in Plone, you can download it from "
        "http://kupu.oscom.org/"),
        severity=logging.INFO, optional=1)

try:
    import Products.PlacelessTranslationService
except ImportError:
    log(("Placeless Translation Service not found. Plone "
         "runs without this, but if you want multilingual "
         "interface or access keys, you must download it from "
         "http://plone.org/products/pts/"),
        severity=logging.INFO, optional=1)

try:
    import Products.PloneTranslations
except ImportError:
    log(("PloneTranslation product with i18n files not found. Plone "
         "runs without this, but if you want multilingual "
         "interface or access keys, you must download it from "
         "http://plone.org/products/plonetranslations"),
        severity=logging.INFO, optional=1)

try:
    import Products.CMFFormController
except ImportError:
    log(("CMFFormController not found. Please "
         "download it from http://plone.org/products/cmfformcontroller"))

try:
    import Products.SecureMailHost
except ImportError:
    log(("SecureMailHost not found. Please "
         "http://plone.org/products/securemailhost"))

try:
    import Products.MimetypesRegistry
except ImportError:
    log(("MimetypesRegistry not found. Please "
         "download it from http://plone.org/products/archetypes"))

try:
    import Products.PortalTransforms
except ImportError:
    log(("PortalTransforms not found. Please "
         "download it from http://plone.org/products/archetypes"))

try:
    import Products.Archetypes
except ImportError:
    # TODO we might want to check the AT version
    log(("Archetypes not found. Please "
         "download it from http://plone.org/products/archetypes"))

try:
    import Products.ATContentTypes.content.document
except ImportError:
    log(("ATContentTypes not found or too old. Please "
         "download it from http://plone.org/products/atcontenttypes"))

try:
    import Products.ExtendedPathIndex
except ImportError:
    log(("ExtendedPathIndex not found. "
         "Please download it from http://plone.org/products/extendedpathindex"))

try:
    import Products.ResourceRegistries
except ImportError:
    log(("ResourceRegistries not found. "
         "Please download it from http://plone.org/products/resourceregistries"))

try:
    import Products.CMFDynamicViewFTI
except ImportError:
    log(("CMFDynamicViewFTI not found. "
         "Please download it from http://plone.org/products/cmfdynamicviewfti"))

try:
    import Products.PlonePAS
except ImportError:
    log(("PlonePAS not found."
         "Please download it from http://plone.org/products/plonepas"))

