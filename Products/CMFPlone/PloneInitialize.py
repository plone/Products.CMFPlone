from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Products.SiteAccess.SiteRoot import manage_addSiteRoot
from Products.SiteAccess.AccessRule import manage_addAccessRule
import transaction

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

def create(app, admin_username='admin'):
    out = []
    oids = app.objectIds()

    # these are the two set elements...
    # (accessRule.py external method and SiteRoot)
    eid = 'accessRule.py'
    pid = 'Plone'
    emod = 'CMFPlone.accessRule'
    efn = 'accessRule'
    sid = 'SiteRoot'

    if pid in oids:
        out.append("A Plone site already exists")
        return out

    # 1 .get the admin user (dont bother making it, it's done before you
    #                        get a chance)

    acl_users = app.acl_users
    user = acl_users.getUser(admin_username)
    if user:
        user = user.__of__(acl_users)
        newSecurityManager(None, user)
        out.append("Retrieved the admin user")
    else:
        out.append("Retrieving admin user failed")

    # 2. create the access rule external method
    if eid not in oids:
        # this is the actual access rule
        manage_addExternalMethod(app,
                                 eid,
                                 'Plone Access Rule',
                                 emod,
                                 efn)
        out.append("Added external method")
        # this sets the access rule
        manage_addAccessRule(app, eid)
        out.append("Set an access rule")

    # 3. actually add in Plone
    if pid not in oids:
        factory = app.manage_addProduct['CMFPlone']
        factory.addPloneSite(pid, create_userfolder=1)
        out.append("Added Plone")

    # 4. adding the site root in
    plone = getattr(app, pid)
    if sid not in plone.objectIds():
        manage_addSiteRoot(plone)
        out.append("Added Site Root")

    # 5. add in products
    qit = plone.portal_quickinstaller

    products_to_install = ["kupu",]
    ids = [ x['id'] for x in qit.listInstallableProducts(skipInstalled=1) ]
    for product in products_to_install:
        if product in ids:
            qit.installProduct(product)

    # 6. commit
    transaction.commit()

    noSecurityManager()
    out.append("Finished")
    return out
