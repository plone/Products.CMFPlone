from Products.MimetypesRegistry.Extensions.Install import fixUpSMIGlobs

def final_two11(portal):
    """2.1-final -> 2.1.1
    """
    fixUpSMIGlobs(portal)
