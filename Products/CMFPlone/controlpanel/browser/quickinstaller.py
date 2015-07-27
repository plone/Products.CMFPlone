from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import INonInstallable
from Products.Five.browser import BrowserView
from Products.GenericSetup import EXTENSION
from Products.statusmessages.interfaces import IStatusMessage
from plone.memoize import view
from zope.component import getAllUtilitiesRegisteredFor
import logging


class ManageProductsView(BrowserView):
    """
    Activate and deactivate products in mass, and without weird
    permissions issues
    """

    def __init__(self, *args, **kwargs):
        super(ManageProductsView, self).__init__(*args, **kwargs)
        self.qi = getToolByName(self.context, 'portal_quickinstaller')
        self.ps = getToolByName(self.context, 'portal_setup')

    def __call__(self):
        return self.index()

    @view.memoize
    def marshall_addons(self):
        addons = {}

        ignore_profiles = []
        utils = getAllUtilitiesRegisteredFor(INonInstallable)
        for util in utils:
            ignore_profiles.extend(util.getNonInstallableProfiles())

        profiles = self.ps.listProfileInfo()
        for profile in profiles:
            if profile['type'] != EXTENSION:
                continue

            pid = profile['id']
            if pid in ignore_profiles:
                continue
            pid_parts = pid.split(':')
            if len(pid_parts) != 2:
                logging.error("Profile with id '%s' is invalid." % pid)
            product_id = profile['product']
            profile_type = pid_parts[-1]
            if product_id not in addons:
                # get some basic information on the product
                product_file = self.qi.getProductFile(product_id)
                installed = False
                upgrade_info = None
                p_obj = self.qi._getOb(product_id, None)
                if p_obj:
                    # TODO; if you install then uninstall, the
                    # presence lingers in the qi. Before it is
                    # run the very first time, it doesn't exist
                    # at all in the qi. How remove the qi from this?
                    installed = p_obj.isInstalled()
                    upgrade_info = self.qi.upgradeInfo(product_id)
                else:
                    # XXX: holy rabbit hole batman!
                    if not self.qi.isProductInstallable(product_id):
                        continue

                if profile_type in product_id:
                    profile_type = 'default'
                    # XXX override here so some products that do not
                    # explicitly say "default" for their install
                    # profile still work
                    # I'm not sure this is right but this is a way
                    # to get CMFPlacefulWorkflow to show up in addons
                    # If it's safe to rename profiles, we can do that too

                addons[product_id] = {
                    'id': product_id,
                    'title': product_id,
                    'description': '',
                    'product_file': product_file,
                    'upgrade_profiles': {},
                    'other_profiles': [],
                    'install_profile': None,
                    'uninstall_profile': None,
                    'is_installed': installed,
                    'upgrade_info': upgrade_info,
                    'profile_type': profile_type,
                }
            product = addons[product_id]
            if profile_type == 'default':
                product['title'] = profile['title']
                product['description'] = profile['description']
                product['install_profile'] = profile
                product['profile_type'] = profile_type
            elif profile_type == 'uninstall':
                product['uninstall_profile'] = profile
                if 'profile_type' not in product:
                    # if this is the only profile installed, it could just be an uninstall
                    # profile
                    product['profile_type'] = profile_type
            else:
                if 'version' in profile:
                    product['upgrade_profiles'][profile['version']] = profile
                else:
                    product['other_profiles'].append(profile)
        return addons

    def get_addons(self, apply_filter=None, product_name=None):
        """
        100% based on generic setup profiles now. Kinda.
        For products magic, use the zope quickinstaller I guess.

        @filter:= 'installed': only products that are installed
                  'upgrades': only products with upgrades
                  'available': products that are not installed bit
                               could be
                  'broken': uninstallable products with broken 
                            dependencies

        @product_name:= a specific product id that you want info on. Do
                   not pass in the profile type, just the name

        XXX: I am pretty sure we don't want base profiles ...
        """
        addons = self.marshall_addons()
        filtered = {}
        if apply_filter == 'broken':
            all_broken = self.qi.getBrokenInstalls()
            for broken in all_broken:
                filtered[broken['productname']] = broken
        else:
            for product_id, addon in addons.items():
                if product_name and addon['id'] != product_name:
                    continue

                installed = addon['is_installed']
                if apply_filter in ['installed', 'upgrades'] and not installed:
                    continue
                elif apply_filter == 'available':
                    if installed:
                        continue
                    # filter out upgrade profiles
                    if addon['profile_type'] != 'default':
                        continue
                elif apply_filter == 'upgrades':
                    # weird p.a.discussion integration behavior
                    upgrade_info = addon['upgrade_info']
                    if type(upgrade_info) == bool:
                        continue

                    if not upgrade_info['available']:
                        continue

                filtered[product_id] = addon

        return filtered

    def get_upgrades(self):
        """
        Return a list of products that have upgrades on tap
        """
        return self.get_addons(apply_filter='upgrades').values()

    def get_installed(self):
        return self.get_addons(apply_filter='installed').values()

    def get_available(self):
        return self.get_addons(apply_filter='available').values()

    def get_broken(self):
        return self.get_addons(apply_filter='broken').values()

    def upgrade_product(self, product):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        messages = IStatusMessage(self.request)
        try:
            qi.upgradeProduct(product)
            messages.addStatusMessage(
                _(u'Upgraded ${product}!', mapping={'product': product}), type="info")
            return True
        except Exception, e:
            logging.error("Could not upgrade %s: %s" % (product, e))
            messages.addStatusMessage(
                _(u'Error upgrading ${product}.', mapping={'product': product}), type="error")

        return False


class UpgradeProductsView(BrowserView):
    """
    Upgrade a product... or twenty
    """
    def __call__(self):
        qi = ManageProductsView(self.context, self.request)
        products = self.request.get('prefs_reinstallProducts', None)
        if products:
            for product in products:
                qi.upgrade_product(product)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/prefs_install_products_form')


class InstallProductsView(BrowserView):

    def __call__(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        products = self.request.get('install_products')
        msg_type = 'info'
        if products:
            messages = IStatusMessage(self.request)
            for product in products:
                qi.installProducts(products=[product, ])
                msg = _(u'Installed ${product}!', mapping={'product': product})
                messages.addStatusMessage(msg, type=msg_type)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/prefs_install_products_form')


class UninstallProductsView(BrowserView):
    def __call__(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        products = self.request.get('uninstall_products')
        msg_type = 'info'
        if products:
            messages = IStatusMessage(self.request)
            # 1 at a time for better error messages
            for product in products:
                try:
                    qi.uninstallProducts(products=[product, ])
                    msg = _(u'Uninstalled ${product}.', mapping={'product': product})
                except Exception, e:
                    logging.error("Could not uninstall %s: %s" % (product, e))
                    msg_type = 'error'
                    msg = _(u'Error uninstalling ${product}.', mapping={'product': product})
                messages.addStatusMessage(msg, type=msg_type)

        purl = getToolByName(self.context, 'portal_url')()
        self.request.response.redirect(purl + '/prefs_install_products_form')
