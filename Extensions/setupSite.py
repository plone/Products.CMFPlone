import os
import sys

def process(name, ihome, swhome):
    admin_username = name
    os.environ['INSTANCE_HOME'] = ihome

    if sys.platform == 'win32':
        sys.path.insert(0, '%s/Zope/lib/python' % swhome)
        sys.path.insert(1, '%s/Python/lib' % swhome)
        sys.path.insert(2, '%s' % swhome)
    else:    
        os.environ['SOFTWARE_HOME'] = swhome
        
    # have to set up env first
    from App import FindHomes
    import Zope

    app = Zope.app()
    
    from OFS.Application import initialize
    initialize(app)

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
    name, swhome, ihome = sys.argv[1:]
    process(name, ihome, swhome)