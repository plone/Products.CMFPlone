import os

def get_version():
    # you run python Extensions/package_plone.py from CMFPlone
    f=open('version.txt', 'r')
    return f.read().strip()

release=get_version()
releasename='CMFPlone-%s' % release
releasetar='CMFPlone%s.tar' % release
releasezip='CMFPlone%s.zip' % release

sh_cleanmisc = """find . | grep '~' | xargs rm -rf"""
sh_cleanpyc = """find . | grep 'pyc' | xargs rm -rf"""
sh_cleancvs = """ find . | grep 'CVS' | xargs rm -rf"""
sh_cleanpyo = """find . | grep 'pyo' | xargs rm -rf"""

os.system("cd ..; rm -rf " + releasetar)

os.system("cd .. ; mkdir " + releasename)
os.system("cd .. ; cp -rfL CMFPlone " + releasename)
os.system("cd .. ; cp -rfL Formulator " + releasename)
os.system("cd .. ; cp -rfL CMFActionIcons " + releasename)
os.system("cd .. ; cp -rfL CMFQuickInstallerTool " + releasename)
os.system("cd .. ; cp -rfL BTreeFolder2 " + releasename)
os.system("cd .. ; cp -rfL GroupUserFolder " + releasename)
os.system("cd .. ; cp -rfL CMFFormController " + releasename)
os.system("cd .. ; cp -rfL PlacelessTranslationService " + releasename)
os.system("cd .. ; cp -rfL i18n " + releasename + '/CMFPlone')

os.system("cd ../" + releasename+";" + sh_cleanmisc)
os.system("cd ../" + releasename+";" + sh_cleanpyc)
os.system("cd ../" + releasename+";" + sh_cleancvs)

os.system("cd .. ; tar -cvf %s %s" % ( releasetar
                                     , releasename ) )
os.system("cd .. ; gzip %s " % releasetar )
os.system("cd .. ; zip -r %s %s" % (releasezip
                                    , releasename ))
