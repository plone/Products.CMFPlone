## Script (Python) "sortObjectValues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=objVals=[]
##title=sorts and pre-filters objects
##
sorted=()

if objVals:
    objVals.sort( lambda x, y: cmp(x.title_or_id().lower(),y.title_or_id().lower()))

sorted=objVals[:]

return sorted
