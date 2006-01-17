from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct
import transaction


def two5_alpha1(portal):
    """2.1.2 -> 2.5-alpha1
    """
    out = [ ]

    # Install PlonePAS
    installPlonePAS(portal, out)

    transaction.commit(1)
    
    return out


def installPlonePAS(portal, out):
    """Quickinstalls PlonePAS if not installed yet."""
    installOrReinstallProduct(portal, 'PlonePAS', out)
