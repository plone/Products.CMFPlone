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
    import Zope2

    configfile = os.path.join(ihome, 'etc', 'zope.conf')

    # nuke remaining command line arguments
    sys.argv = sys.argv[:1]

    # for 2.7 run configure
    Zope2.configure(configfile)
    app = Zope2.app()

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
    name, swhome, ihome = sys.argv[1:]
    process(name, swhome, ihome)
