import os
import sys

def process(name, swhome, ihome):
    admin_username = name
    os.environ['INSTANCE_HOME'] = ihome

    if sys.platform == 'win32':
        sys.path.insert(0, '%s/Zope/lib/python' % swhome)
        sys.path.insert(1, '%s/Python/lib' % swhome)
        sys.path.insert(2, '%s' % swhome)
    else:
        os.environ['SOFTWARE_HOME'] = swhome
        sys.path.insert(0, '%s' % swhome)

    # have to set up env first
    import Zope

    # http://mail.zope.org/pipermail/zope-dev/2003-August/020274.html
    # this is annoying, but works, hopefully this can be removed in the near
    # future
    from App import FindHomes
    from Zope.Startup.options import ZopeOptions
    from Zope.Startup import handlers as h
    from App import config
    opts = ZopeOptions()
    # its going to look for zope.conf in instance home
    opts.configfile = os.path.join(ihome,'etc/zope.conf')
    sys.argv = sys.argv[:1]
    opts.realize()
    h.handleConfig(opts.configroot,opts.confighandlers)
    config.setConfiguration(opts.configroot)
    # end hack    

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
    # like it says above, win32 is different
    # example for Mac OS X (and probably all nix-based OS, adjust paths as required, note "Default" is INSTANCE_HOME and contains Extensions/import/var/Products etc):
    # /Applications/Plone2/Software/Zope262/Python/bin/python setupSite.py admin /Applications/Plone2/Software/Zope262/Zope/lib/python /Applications/Plone2/Sites/Default
    name, swhome, ihome = sys.argv[1:]
    process(name, swhome, ihome)
