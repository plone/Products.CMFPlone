#!/usr/bin/env python
import os

def get_version():
    # you run python Extensions/package_plone.py from CMFPlone
    f=open('version.txt', 'r')
    return f.read().strip()

release=get_version()
releasename='CMFPlone-%s' % release
releasetar='CMFPlone-%s.tar.gz' % release
releasezip='CMFPlone-%s.zip' % release

corename='PloneBase-%s' % release
coretar='PloneBase-%s.tar.gz' % release
corezip='PloneBase-%s.zip' % release

# cleans pyc, pyo, temp files, CVS files and compiled po files
sh_clean = """find . -name *.py[co] -or -name *~ -or -name ~* -or -name CVS -or \
                     -name .#* -or -name .cvsignore -or -name *.mo| xargs rm -rf"""

assert len(os.listdir('i18n')) > 1, "Ensure the i18n files from the sf project are placed into the i18n directory"                     
                     
# remove old stuff, create new directory
os.system("cd ..; rm -rf %s %s %s" % (releasetar, releasezip, releasename))
os.system("cd ..; rm -rf %s %s" % (coretar, corezip))
os.system("cd .. ; mkdir %s" % releasename)

# copy products
for product in ('CMFPlone', 'Formulator', 'CMFActionIcons', 'CMFQuickInstallerTool',
                'BTreeFolder2', 'GroupUserFolder', 'CMFFormController',
                'PlacelessTranslationService', 'Archetypes', 'generator', 'validation',
                'PortalTransforms', 'CMFCore', 'CMFDefault', 'CMFCalendar', 'DCWorkflow',
                'CMFTopic', 'PloneErrorReporting'):
    os.system("cd .. ; cp -rfL %s %s" % (product, releasename))

# clean up
os.system("cd ../%s; %s"  % (releasename, sh_clean))

# make tar.gz
os.system("cd .. ; tar -f %s -czv %s " % ( releasetar
                                     , releasename ) )
# make zip
os.system("cd .. ; zip -r %s %s" % (releasezip
                                    , releasename ))

# build PloneCore tarball
# make tar.gz
os.system("cd ../%s ; tar -f %s -czv %s; mv %s .. " % ( releasename, coretar
                                     , "CMFPlone", coretar ) )

# make zip                                     
os.system("cd ../%s ; zip -r %s %s; mv %s .. " % ( releasename, corezip
                                     , "CMFPlone", corezip ) )                   