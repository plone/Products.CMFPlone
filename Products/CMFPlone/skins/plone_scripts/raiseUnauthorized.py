## Script (Python) "raiseUnauthorized"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=

from AccessControl import Unauthorized

raise Unauthorized
