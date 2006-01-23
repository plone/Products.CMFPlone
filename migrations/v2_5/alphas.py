from Products.CMFPlone.migrations.migration_util import installOrReinstallProduct

def two5_alpha1(portal):
    """2.1.2 -> 2.5-alpha1
    """
    out = []

    # Install CMFPlacefulWorkflow
    installPlacefulWorkflow(portal, out)

    return out


def installPlacefulWorkflow(portal, out):
    """Quickinstalls CMFPlacefulWorkflow if not installed yet."""
    # CMFPlacefulWorkflow is optional
    try:
        import Products.CMFPlacefulWorkflow
    except ImportError:
        pass
    else:
        # CMFPlacefulWorkflow is not installed by e.g. tests
        if 'CMFPlacefulWorkflow' in portal.Control_Panel.Products.objectIds():
            installOrReinstallProduct(portal, 'CMFPlacefulWorkflow', out)
