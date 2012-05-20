## Script (Python) "prefs_valid_search_restriction.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=searchonly, specified=['users','groups']
##title=Valid Search Resriction

# 'specified' must be a list
return ((searchonly != None) and (searchonly in specified))
