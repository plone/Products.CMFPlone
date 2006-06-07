from Products.CMFCore.utils import getToolByName

def beta2_rc1(portal):
    """2.5-beta2 -> 2.5-rc1
    """
    out = []
    # add a property indicating if this is a big or small site, so the UI can
    # change depending on it
    propTool = getToolByName(portal, 'portal_properties', None)
    propSheet = getattr(propTool, 'site_properties', None)
    if not propSheet.hasProperty('many_users'):
        if propSheet.hasProperty('large_site'):
            out.append("Migrating 'large_site' to 'many_users' property.")
            default=propSheet.getProperty('large_site')
            propSheet.manage_delProperties(ids=['large_site'])
        else:
            default=0
        propSheet.manage_addProperty('many_users', default, 'boolean')
        out.append("Added 'many_users' property to site_properties.")

def rc1_final(portal):
    """2.5-rc1 -> 2.5.0
    """
    out = []
    addNavtreeCSS(portal, out)

    return out

def addNavtreeCSS(portal, out):
    # add new css files to the portal_css registries
    cssreg = getToolByName(portal, 'portal_css', None)
    stylesheet_ids = cssreg.getResourceIds()
    if 'navtree.css' not in stylesheet_ids:
        cssreg.registerStylesheet('navtree.css', media='screen')
        cssreg.moveResourceAfter('navtree.css', 'textLarge.css')
        out.append("Added navtree.css to the registry")
    if 'invisibles.css' not in stylesheet_ids:
        cssreg.registerStylesheet('invisibles.css', media='screen')
        cssreg.moveResourceAfter('invisibles.css', 'navtree.css')
        out.append("Added invisibles.css to the registry")
    if 'forms.css' not in stylesheet_ids:
        cssreg.registerStylesheet('forms.css', media='screen')
        cssreg.moveResourceAfter('forms.css', 'invisibles.css')
        out.append("Added forms.css to the registry")

