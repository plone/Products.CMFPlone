## Script (Python) "log_error"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=error, template
##title=Logger script for tal:on-error
##
from zLOG import LOG, WARNING

# usage:
# tal:on-error="here.log_error(error, template)"

type    = error.type
value   = error.value
lineno  = error.lineno
offset  = error.offset

summary = '%s: %s, at line %s, column %s' % (str(type), str(value), lineno, offset)
text    = 'The error was catched in the template %s' % template.absolute_url(1)

# XXX why the heck isn't it logging?
LOG('CMFPlone', WARNING, summary, text)
