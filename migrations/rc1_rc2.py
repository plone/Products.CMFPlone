from migration_util import safeEditProperty

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
    for k, v in changes.items():
        safeEditProperty(nav_props, k, v)

    pg=PloneGenerator()
    sk_tool=getToolByName(portal, 'portal_skins')
    setup_skins=pg.setupSecondarySkin
    setup_skins(sk_tool, 'Plone Core',          'plone_styles/core')
    setup_skins(sk_tool, 'Plone Corporate',     'plone_styles/corporate') 
    #new for 1.0/RC2
    setup_skins(sk_tool, 'Plone Autumn',        'plone_styles/autumn')
    setup_skins(sk_tool, 'Plone Core Inverted', 'plone_styles/core_inverted')
    setup_skins(sk_tool, 'Plone Greensleeves',  'plone_styles/greensleeves')
    setup_skins(sk_tool, 'Plone Kitty',         'plone_styles/kitty')
    setup_skins(sk_tool, 'Plone Mozilla New',   'plone_styles/mozilla_new')
    setup_skins(sk_tool, 'Plone Prime',         'plone_styles/prime')
    setup_skins(sk_tool, 'Plone Zed',           'plone_styles/zed')

    #prematurely put some properties in.. which was very naughty
    try:
        s_props=portal.portal_properties.site_properties
        s_props._delProperty('validate_email')
        s_props._delProperty('email_from_address')
        s_props._delProperty('email_from_name')
    except:
        pass #XXX its easier
	
