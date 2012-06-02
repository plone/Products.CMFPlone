from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFPlone.PloneBaseTool import PloneBaseTool
from Products.CMFQuickInstallerTool.QuickInstallerTool \
    import QuickInstallerTool as BaseTool
from Products.CMFQuickInstallerTool.interfaces import IQuickInstallerTool
import pkg_resources


class QuickInstallerTool(PloneBaseTool, BaseTool):
    """ A tool to ease installing/uninstalling all sorts of products """

    meta_type = 'Plone QuickInstaller Tool'
    security = ClassSecurityInfo()
    toolicon = 'skins/plone_images/product_icon.png'

    security.declareProtected(ManagePortal, 'upgradeInfo')
    def upgradeInfo(self, pid):
        """Returns a dict with two booleans values, stating if an upgrade
        is required and available.
        """
        available = self.isProductAvailable(pid)
        if not available:
            return False
        # Product version as per version.txt or fallback on metadata file
        product_version = str(self.getProductVersion(pid))
        installed_product_version = self._getOb(pid).getInstalledVersion()
        profile = self.getInstallProfile(pid)
        if profile is None:
            # No GS profile, simple case as before, we can always upgrade
            return dict(
                required=product_version != installed_product_version,
                available=True,
                hasProfile=False,
                installedVersion=installed_product_version,
                newVersion=product_version,
                )
        profile_id = profile['id']
        setup = getToolByName(self, 'portal_setup')
        profile_version = str(setup.getVersionForProfile(profile_id))
        if profile_version == 'latest':
            profile_version = self.getLatestUpgradeStep(profile_id)
        if profile_version == 'unknown':
            # If a profile doesn't have a metadata.xml use product version
            profile_version = product_version
        installed_profile_version = setup.getLastVersionForProfile(profile_id)
        # getLastVersionForProfile returns the version as a tuple or unknown.
        if installed_profile_version != 'unknown':
            installed_profile_version = str(
                '.'.join(installed_profile_version))
        return dict(
            required=profile_version != installed_profile_version,
            available=len(setup.listUpgrades(profile_id)) > 0,
            hasProfile=True,
            installedVersion=installed_profile_version,
            newVersion=profile_version,
            )

    security.declareProtected(ManagePortal, 'getLatestUpgradeStep')
    def getLatestUpgradeStep(self, profile_id):
        '''
        Get the highest ordered upgrade step available to
        a specific profile.

        If anything errors out then go back to "old way"
        by returning 'unknown'
        '''
        setup = getToolByName(self, 'portal_setup')
        profile_version = 'unknown'
        try:
            available = setup.listUpgrades(profile_id, True)
            if available:  # could return empty sequence
                latest = available[-1]
                profile_version = max(latest['dest'],
                        key=pkg_resources.parse_version)
        except Exception:
            pass

        return profile_version

    security.declareProtected(ManagePortal, 'upgradeProduct')
    def upgradeProduct(self, pid):
        profile = self.getInstallProfile(pid)
        if profile is None:
            # No upgrade profiles
            return self.reinstallProducts(products=[pid])
        profile_id = profile['id']
        setup = getToolByName(self, 'portal_setup')
        upgrades = setup.listUpgrades(profile_id)
        for upgrade in upgrades:
            # An upgrade may be a single step (for a bare upgradeStep)
            # or a list of steps (for upgradeSteps containing upgradeStep
            # directives).
            if not type(upgrade) is list:
                upgrade = [upgrade]
            for upgradestep in upgrade:
                step = upgradestep['step']
                step.doStep(setup)
        version = str(profile['version'])
        if version == 'latest':
            version = self.getLatestUpgradeStep(profile_id)
        setup.setLastVersionForProfile(profile_id, version)


QuickInstallerTool.__doc__ = BaseTool.__doc__

InitializeClass(QuickInstallerTool)
registerToolInterface('portal_quickinstaller', IQuickInstallerTool)
