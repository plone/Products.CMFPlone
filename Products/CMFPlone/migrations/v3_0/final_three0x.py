from Products.CMFPlone.migrations.migration_util import loadMigrationProfile


def final_three01(portal):
    
    out = []
    
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0final-3.0.1')
    
    return out

def three01_three02(portal):
    
    out = []
    
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0.1-3.0.2')
    
    return out

def three03_three04(portal):
    
    out = []
    
    loadMigrationProfile(portal, 'profile-Products.CMFPlone.migrations:3.0.3-3.0.4')
    
    return out

