import os

release='1.0.1'
releasename='CMFPlone-%s' % release
releasetar='CMFPlone%s.tar' % release

sh_cleanmisc = """find . | grep '~' | xargs rm -rf"""
sh_cleanpyc = """find . | grep 'pyc' | xargs rm -rf"""
sh_cleancvs = """ find . | grep 'CVS' | xargs rm -rf"""

os.system("cd ..; rm -rf " + releasetar)

os.system("cd .. ; mkdir " + releasename)
os.system("cd .. ; cp -rf CMFPlone " + releasename)
os.system("cd .. ; cp -rf Formulator " + releasename)
os.system("cd .. ; cp -rf DCWorkflow " + releasename)

os.system("cd ../" + releasename+";" + sh_cleanmisc)
os.system("cd ../" + releasename+";" + sh_cleanpyc)
os.system("cd ../" + releasename+";" + sh_cleancvs)

os.system("cd .. ; tar -cvf %s %s" % ( releasetar 
                                     , releasename ) )
os.system("cd .. ; gzip %s " % releasetar )


