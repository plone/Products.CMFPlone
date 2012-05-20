## Script (Python) "isTranslatable"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

from ZODB.POSException import ConflictError

try:
    return context.portal_url.getPortalObject().plone_utils \
                .isTranslatable(context)
except ConflictError:
    raise
except:
    return 0
