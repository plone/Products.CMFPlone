from Products.CMFPlone import MigrationTool
from Products.CMFPlone.Portal import PloneGenerator
from Products.CMFPlone.CustomizationPolicy import DefaultCustomizationPolicy
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import getToolByName

def rc1rc2(portal):
    """ Upgrade from Plone 1.0 RC1 to RC2 """

    #adding navigation properties
    nav_props=portal.portal_properties.navigation_properties
    changes={'default.folder_rename_form.success':'script:folder_rename',
             'default.personalize.success':'personalize_form'}
    nav_props.manage_changeProperties(changes)

    pg=PloneGenerator()
    sk_tool=getToolByName(portal, 'portal_skins')
    setup_skins=pg.setupSecondarySkin
    #original
    setup_skins(sk_tool, 'Plone Core',          'plone_styles/core')
    setup_skins(sk_tool, 'Plone Corporate',     'plone_styles/corporate') #formerly PloneXP
    #new for 1.0/RC2
    setup_skins(sk_tool, 'Plone Autumn',        'plone_styles/autumn')
    setup_skins(sk_tool, 'Plone Core Inverted', 'plone_styles/core_inverted')
    setup_skins(sk_tool, 'Plone Greensleeves',  'plone_styles/greensleeves')
    setup_skins(sk_tool, 'Plone Kitty',         'plone_styles/kitty')
    setup_skins(sk_tool, 'Plone Mozilla New',   'plone_styles/mozilla_new')
    setup_skins(sk_tool, 'Plone Prime',         'plone_styles/prime')
    setup_skins(sk_tool, 'Plone Zed',           'plone_styles/zed')

def registerMigrations():
    # so the basic concepts is you put a bunch of migrations is here
    MigrationTool.registerUpgradePath(
            '1.0RC1', 
            '1.0RC2', 
            rc1rc2
            )

if __name__=='__main__':
    registerMigrations()

