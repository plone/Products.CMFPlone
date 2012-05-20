## Script (Python) "prefs_reinstallProducts"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=prefs_reinstallProducts

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

req = context.REQUEST

qi = getToolByName(context, 'portal_quickinstaller')
putil = getToolByName(context, 'plone_utils')

product = req.get('prefs_reinstallProducts', None)
if product:
    qi.upgradeProduct(product)
    msg = _(u'Upgraded ${product}', mapping={'product': product})
    putil.addPortalMessage(msg)

purl = getToolByName(context, 'portal_url')()
req.response.redirect(purl + '/prefs_install_products_form')

return 'Redirecting ...'
