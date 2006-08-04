from Products.CMFCore.utils import getToolByName

def final_two51(portal):
    """2.5-final -> 2.5.1
    """
    out = []
    removePloneCssFromRR(portal, out)

    return out

def removePloneCssFromRR(portal, out):
    """Removes the redundant, deprecated, and failing plone.css from portal_css.
       It is a python script now and just calls portal_css itself."""
    css_reg = getToolByName(portal, 'portal_css', None)
    if css_reg is not None:
        stylesheet_ids = css_reg.getResourceIds()
        if 'plone.css' in stylesheet_ids:
            css_reg.unregisterResource('plone.css')
            out.append('Unregistered deprecated plone.css')
