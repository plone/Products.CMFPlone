from Products.CMFCore.utils import getToolByName

PROF_ID = 'Products.CMFPlone:plone'

def two53_two54(portal):
    """2.5.3 -> 2.5.4
    """
    out = []
    addGSSteps(portal, out)

    return out


def addGSSteps(portal, out):
    """ Add import export steps in GS """
    setup_tool = getToolByName(portal, 'portal_setup', None)
    if setup_tool is not None:
        # only reun when unset
        if not setup_tool.getImportContextID():
            # make sure the profile is there
            if PROF_ID in [i['id'] for i in setup_tool.listProfileInfo()]:
                setup_tool.setImportContext(PROF_ID)
    out.append('Set plone GS profile as default')
