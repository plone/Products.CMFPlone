import os

release='1.0.1'
releasename='CMFPlone-%s' % release
releasetar='CMFPlone%s.tar' % release

sh_cleanmisc = """find . -name '*~' | xargs rm -rf"""
sh_cleanpyc = """find . -name '*\.pyc' | xargs rm -rf"""
sh_cleancvs = """ find . -name 'CVS' | xargs rm -rf"""
sh_cleanhidden = """ find . -name '\.#*' | xargs rm -rf"""

os.system("cd ..; rm -rf " + releasetar)
os.system("cd ..; rm -rf " + releasename)

os.system("cd .. ; mkdir " + releasename)
os.system("cd .. ; cp -rfL CMFPlone " + releasename)
os.system("cd .. ; cp -rfL Formulator " + releasename)
os.system("cd .. ; cp -rfL DCWorkflow " + releasename)

os.system("cd ../" + releasename+";" + sh_cleanmisc)
os.system("cd ../" + releasename+";" + sh_cleanpyc)
os.system("cd ../" + releasename+";" + sh_cleancvs)
os.system("cd ../" + releasename+";" + sh_cleanhidden)

os.system("cd .. ; tar -cvf %s %s" % ( releasetar 
                                     , releasename ) )
os.system("cd .. ; gzip %s " % releasetar )


