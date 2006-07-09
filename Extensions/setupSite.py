import os
import sys

def process(name, swhome, ihome):
    admin_username = name
    os.environ['INSTANCE_HOME'] = ihome

    if sys.platform == 'win32':
        sys.path.insert(0, os.path.join(swhome, 'Zope', 'lib', 'python'))
        sys.path.insert(1, os.path.join(swhome, 'Python', 'lib'))
        sys.path.insert(2, swhome)
    else:
        os.environ['SOFTWARE_HOME'] = swhome
        sys.path.insert(0, swhome)

    # have to set up env first
    try:
        # Zope 2.8 on, Zope is now 'Zope2' and 'zope' is the Zope 3
        # libs.
        import Zope2 as Zope
    except ImportError:
        import Zope

    configfile = os.path.join(ihome, 'etc', 'zope.conf')

    # nuke remaining command line arguments
    sys.argv = sys.argv[:1]

    # for 2.7 run configure
    Zope.configure(configfile)
    app = Zope.app()

    from Testing import makerequest
    app = makerequest.makerequest(app)

    from Products.CMFPlone.PloneInitialize import create
    out = create(app, admin_username)
    return out

if __name__=='__main__':
    # sys.argv[0] is script name
    if len(sys.argv) < 4:
        print """
setupSite.py username swhome ihome

username: the username to setup the site with
swhome: the software home
ihome: the instance home

note: win32 does this slightly differently
"""
        sys.exit()

    # for example the following is how i run it on win32
    # "c:\Program Files\Plone\python\python" setupSite.py admin "c:\Program Files\Plone\Data" "c:\Program Files\Plone"
    # like it says above, win32 is different
    # example for Mac OS X (and probably all nix-based OS, adjust paths as required, note "Default" is INSTANCE_HOME and contains Extensions/import/var/Products etc):
    # /Applications/Plone2/Software/Zope262/Python/bin/python setupSite.py admin /Applications/Plone2/Software/Zope262/Zope/lib/python /Applications/Plone2/Sites/Default
    name, swhome, ihome = sys.argv[1:]
    process(name, swhome, ihome)
