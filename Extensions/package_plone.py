import os

release='1.0alpha3'

sh_cleanmisc = """find . | grep '~' | xargs rm -rf"""
sh_cleanpyc = """find . | grep 'pyc' | xargs rm -rf"""

os.system(sh_cleanmisc)
os.system(sh_cleanpyc)

os.system("cd .. ; tar -cvf CMFPlone%s.tar CMFPlone" % release)

