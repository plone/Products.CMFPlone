from Products.CMFPlone import MigrationTool
from Products.CMFPlone.Portal import PloneGenerator
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName
from ZODB.POSException import ConflictError

def rc1rc2(portal):
    """ Upgrade from Plone 1.0 RC1 to RC2 """

    #adding navigation properties
    nav_props=portal.portal_properties.navigation_properties
    changes={'default.folder_rename_form.success':'script:folder_rename',
             'default.personalize.success':'personalize_form'}
    nav_props.manage_changeProperties(changes)

    #prematurely put some properties in.. which was very naughty
    try:
        s_props=portal.portal_properties.site_properties
        s_props._delProperty('validate_email')
        s_props._delProperty('email_from_address')
        s_props._delProperty('email_from_name')
    except ConflictError:
        raise
    except:
        pass # XXX its easier

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations is here
    MigrationTool.registerUpgradePath(
            '1.0RC1',
            '1.0RC2',
            rc1rc2
            )

if __name__=='__main__':
    registerMigrations()
