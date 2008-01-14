from Products.CMFCore.utils import getToolByName


def three1_alpha(portal):
    """Migrations from 3.0.x to 3.1 alpha"""

    out = []
    reinstallCMFPlacefulWorkflow(portal, out)

    return out


def reinstallCMFPlacefulWorkflow(portal, out):
    qi = getToolByName(portal, 'portal_quickinstaller', None)
    if qi is not None:
        installed = qi.isProductInstalled('CMFPlacefulWorkflow')
        if installed:
            qi.reinstallProducts(['CMFPlacefulWorkflow'])
            out.append('Reinstalled CMFPlacefulWorkflow')
