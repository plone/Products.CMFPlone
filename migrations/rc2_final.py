from Products.CMFPlone import MigrationTool

def rc2Final(portal):
    """ Upgrade from Plone 1.0 RC2 to Final"""

    p = portal.portal_properties.site_properties
    e = getattr(p, 'available_editors', [])

    # if there is the old editor in there,
    # change it to the new one
    if 'XSDHTMLEditor' in e:
        e[e.index('XSDHTMLEditor')] = 'Visual Editor'
        p._setProperty('available_editors', e)

def registerMigrations():
    MigrationTool.registerUpgradePath(
            '1.0RC2', 
            '1.0', 
            rc1Final
            )

if __name__=='__main__':
    registerMigrations()

