## Script (Python) "plone_log"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=summary='',text=''
##title=
##
from logging import getLogger
log = getLogger('Plone')
log.info('Debug: %s \n%s', summary, text)
