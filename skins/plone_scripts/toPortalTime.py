## Script (Python) "toPortalTime"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=time=None, long_format=None
##title=
##
#given a time string convert it into a DateTime and then format it appropariately
#
# deprecated, use toLocalizedTime instead
#
return context.toLocalizedTime(time=time, long_format=long_format)
