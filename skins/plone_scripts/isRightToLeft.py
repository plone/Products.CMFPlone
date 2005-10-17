## Script (Python) "isRightToLeft"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=domain
##title=
##
try:
    from Products.PlacelessTranslationService import isRTL
except ImportError:
    # This may mean we have an old version of PTS or no PTS at all.
    return 0
else:
    try:
        return isRTL(context, domain)
    except AttributeError:
        # This may mean that PTS is present but not installed.
        # Can effectively only happen in unit tests.
        return 0
