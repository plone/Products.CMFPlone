from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Products.CMFPlone.Portal import manage_addSite
from Products.SiteAccess.SiteRoot import manage_addSiteRoot
from Products.SiteAccess.AccessRule import manage_addAccessRule
from AccessControl import User

import OFS
import os

from ConfigParser import ConfigParser

# grab the old initilalize...
old_initialize = OFS.Application.initialize

def go(app):
    """ Initialize the ZODB with Plone """
    old_initialize(app)

    # nothing no error at all should
    # stop the creation of the db
    # that would truly suck
    try: _go(app)
    except: pass

def _go(app):
    filename = 'plone.ini'
    filename = os.path.join(INSTANCE_HOME, filename)

    # not the best
    try: 
        fh = open(filename, 'r')
        cfg = ConfigParser()
        cfg.readfp(fh)
        fh.close()
    except NameError: 
        # no file found
        print "No file found"
        return

    
    try:
        pid = cfg.get('databaseSetup', 'name')
        usernm  = cfg.get('databaseSetup', 'user')
        create = cfg.getint('databaseSetup', 'create')
    except ConfigParser.NoSectionError:
        # no section name databaseSetup
        print "NoSectionError"
        return
    except AttributeError:
        # no attribute named 
        print "Attribute Error"
        return

    # ok if create in that file is set to 0, then we dont continue
    if not create:
        print "Not create"
        return

    oids = app.objectIds()

    # these are the two set elements...
    eid = 'accessRule.py'
    sid = 'SiteRoot'

    # 1. Create the admin user given the access file
    acl_users = getattr(app, "acl_users")

    # ugh oh well...
    if usernm not in acl_users.getUserNames():
        # read the file and add in
        info = User.readUserAccessFile('access')
        acl_users._doAddUser(info[0], info[1], ('manage',), [])

    # 2 .now get that user
    user = acl_users.getUser('admin').__of__(acl_users)

    # 3. now create the access rule
    if eid not in oids:
        # this is the actual access rule
        manage_addExternalMethod(app, 
                                                  eid, 
                                                  'Plone Access Rule', 
                                                  'accessRule', 
                                                  'accessRule')
        # this sets the access rule
        manage_addAccessRule(app, eid)
        getattr(app, eid).changeOwnership(user)

    # 4. actually add in Plone
    if pid not in oids:
        manage_addSite(app, 
                   pid, 
                   title='Portal', 
                   description='',
                   create_userfolder=1,
                   email_from_address='postmaster@localhost',
                   email_from_name='Portal Administrator',
                   validate_email=0,
                   custom_policy='',
                   RESPONSE=None)
        getattr(app, pid).changeOwnership(user, recursive=1)

    # 5. adding the site root in
    plone = getattr(app, pid)
    if sid not in plone.objectIds():
        manage_addSiteRoot(plone)
        getattr(plone, sid).changeOwnership(user)

    # and stop this happening again
    cfg.set('databaseSetup', 'create', 0)
    fh = open(filename, 'w')
    cfg.write(fh)
    fh.close()

# patch away!
OFS.Application.initialize = go