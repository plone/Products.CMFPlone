from Products.CMFPlone.migrations.migration_util import loadMigrationProfile

def three11_three12(portal):
    """3.1.1 -> 3.1.2"""
    
    out = []
    
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.1.1-3.1.2')

def three13_three14(portal):
    """3.1.3 -> 3.1.4"""
    
    out = []
    
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.1.3-3.1.4')
