from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Products.CMFPlone.Portal import manage_addSite
from Products.SiteAccess.SiteRoot import manage_addSiteRoot
from Products.SiteAccess.AccessRule import manage_addAccessRule

# add in message catalog stuff
try:
    from Products.Localizer.Localizer import manage_addLocalizer
    from Products.Localizer.MessageCatalog import manage_addMessageCatalog
    hasLocalizer = 1
except ImportError:
    hasLocalizer = 0

from AccessControl import User

from App.Extensions import getObject

import string
import glob 
import OFS
import os
import sys
import zLOG

DEBUG = 0

def log(message, summary='', severity=0):
    zLOG.LOG('Plone Database Init', severity, summary, message)

from ConfigParser import ConfigParser

# grab the old initilalize...
old_initialize = OFS.Application.initialize

# for i18n stuff
i18nDir = os.path.join(INSTANCE_HOME, 'Products', 'i18n')

out = []

def go(app):
    """ Initialize the ZODB with Plone """
    old_initialize(app)

    # nothing no error at all should
    # stop the creation of the db
    # that would truly suck
    try: 
        _go(app)
    except: 
        # oh dear
        out.append('Database init failed miserably [%s, %s]' % _get_error())

    if DEBUG and out:
        # only log if we have something to say
        # and are in DEBUG mode
        log('\n'.join(out)+'\n')

def _get_error():
    type, value = sys.exc_info()[:2]
    return str(type), str(value)

def _installSkins(plone, skinList):
    skin_tool = getattr(plone, 'portal_skins')

   # ripped from Portal.py
    for skin in skinList:
        # cheeky fellow, this is bound to break at some point
        directory_id = 'plone_styles/' + skin[6:].replace(' ', '_').lower()
        path = [elem.strip() for elem in skin_tool.getSkinPath('Plone Default').split(',')]
        path.insert(path.index('custom')+1, directory_id)
        skin_tool.addSkinSelection(skin, ','.join(path))

def _installLocalizer(plone):
    out.append('Installing Localizer')

    lName = 'Localizer'
    tName = 'translation_service'
    
    if not plone.objectIds(lName):
        # add localizer
        manage_addLocalizer(plone, lName, 'en')
        
    if not tName in plone.objectIds():
        # add a translation_service
        plone.manage_addProduct['TranslationService'].addPlacefulTranslationService(tName)

    tObj = plone._getOb(tName)
    lObj = plone._getOb(lName)

    # nuke out the accept_path
    lObj.accept_methods = ['accept_cookie',]

    # ok so now we should have valid localizer
    # and translation service objects...

    manage_addMessageCatalog(lObj, 'Plone', 'Plone Message Catalog', 'en')
    mObj = lObj.Plone

    tObj.manage_setDomainInfo(None, path_0='%s/Plone' % lName) 
    # set the translation_service to the localizer...

    # delete all languages, just in case, for 
    # some reason im getting wierd ones
    mObj.manage_delLanguages(languages=mObj._languages)

    # add in languages
    out.append('Reading .po files from %s' % i18nDir)
    if os.path.exists(i18nDir):
        for file in glob.glob(os.path.join(i18nDir, '*.po')):
            try:
                out.append('Found file: %s' % file)
                fn = os.path.basename(file)
                lang = fn[6:-3]

                # first add in the language
                out.append('Adding language: %s' % lang)
                mObj.manage_addLanguage(lang)
    
                # then add in the file
                out.append('Adding po file')
                fh = open(file, 'rb')
                mObj.manage_import(lang, fh)
            except:
                out.append('Failed to setup .po file for: %s' % file)
    else:
        out.append('No i18n directory found')

    # set the default language to english
    mObj.manage_changeDefaultLang(language='en')

def _go(app):
    filename = 'plone.ini'
    filename = os.path.join(INSTANCE_HOME, filename)

    # not the best
    try: 
        fh = open(filename, 'r')
        cfg = ConfigParser()
        cfg.readfp(fh)
        fh.close()
    except: 
        # no file found
        return

    # read the config file and find a million excuses
    # why we shouldnt do this...
    try:
        pid = cfg.get('databaseSetup', 'name')
        usernm  = cfg.get('databaseSetup', 'user')
        productList = cfg.get('databaseSetup', 'products').split(',')
        create = cfg.getint('databaseSetup', 'create')
        skinList = cfg.get('databaseSetup', 'skins').split(',')
    except ConfigParser.NoSectionError:
        # no section name databaseSetup
        out.append("NoSectionError when parsing config file")
        return
    except AttributeError:
        # no attribute named 
        out.append("AttributeError when parsing config file")
        return

    # ok if create in that file is set to 0, then we dont continue
    if not create:
        out.append("Config file found, but create set to 0")
        return

    oids = app.objectIds()

    # these are the two set elements...
    eid = 'accessRule.py'
    sid = 'SiteRoot'

    # 1. Create the admin user given the access file
    acl_users = getattr(app, "acl_users")

    # ugh oh well...
    try:
        if usernm not in acl_users.getUserNames():
            # read the file and add in
            # inituser is created by the installer
            info = User.readUserAccessFile('inituser')
            if info:
                out.append(str(info))
                acl_users._doAddUser(info[0], info[1], ('manage',), [])
                out.append("Added admin user")
                # important, get that user in there!
                get_transaction().commit()
            else:
                out.append("No inituser file found")
    except:
        out.append("Adding admin user failed [%s, %s]" %  _get_error())

    # 2 .now get that user, it could be that one already exists
    user = acl_users.getUser('admin').__of__(acl_users)
    if not user:
        out.append("Getting user failed [%s, %s]" %  _get_error())
    else:
        out.append("Gotten the admin user")


    # 3. now create the access rule
    if eid not in oids:
        # this is the actual access rule
        out.append("Added external method")
        manage_addExternalMethod(app, 
                                                  eid, 
                                                  'Plone Access Rule', 
                                                  'accessRule', 
                                                  'accessRule')
        # this sets the access rule
        out.append("Set as access rule")
        manage_addAccessRule(app, eid)
        if user:
            getattr(app, eid).changeOwnership(user)

    # 4. actually add in Plone
    if pid not in oids:
        out.append("Added Plone")
        manage_addSite(app, 
                   pid, 
                   title='Portal', 
                   description='',
                   create_userfolder=1,
                   email_from_address='postmaster@localhost',
                   email_from_name='Portal Administrator',
                   validate_email=0,
                   custom_policy='Default Plone',
                   RESPONSE=None)
        if user:
            getattr(app, pid).changeOwnership(user, recursive=1)

    # 5. adding the site root in
    plone = getattr(app, pid)
    if sid not in plone.objectIds():
        out.append("Added Site Root")
        manage_addSiteRoot(plone)
        if user:
            getattr(plone, sid).changeOwnership(user)

    # 6. Install std products
    # this is every product :)
    # productList = app.Control_Panel.Products.objectIds()
    # productList = ['CMFCollector', 'CMFForum']
    for productId in productList:
        try:
            productId = productId.strip()
            res = getObject('%s.Install' % productId, 'install')(plone)
            out.append("Installed %s" % productId)
            out.append("%s: %s" % (productId, res))

        except:
            value, type = _get_error()
            out.append("Failed to install %s, reason:" % (productId, value, type))

    # CMF Collector is a very bad product
    # import workflow
    plone.portal_workflow.manage_importObject('collector_issue_workflow.zexp')
    cbt = plone.portal_workflow._chains_by_type
    cbt['Collector Issue'] = ('collector_issue_workflow',)

    # go and install the skins...
    _installSkins(plone, skinList)

    # Plone is a bad product
    skins = plone.portal_skins.getSkinSelections()
    for skin in skins:
        path = plone.portal_skins.getSkinPath(skin)
        path = map(string.strip, string.split(path,','))
        path.insert(1, 'plone_3rdParty/CMFCollector')
        plone.portal_skins.addSkinSelection(skin, ','.join(path))
    # Sigh, ok now CMFCollector should be in the path

    # go and install the translation service...
    if hasLocalizer:
        _installLocalizer(plone)

    get_transaction().commit()

    # and stop this happening again
    cfg.set('databaseSetup', 'create', 0)
    fh = open(filename, 'w')
    cfg.write(fh)
    out.append("Changed config file, set create = 0")
    fh.close()
    out.append("Finished")

# patch away!
OFS.Application.initialize = go
