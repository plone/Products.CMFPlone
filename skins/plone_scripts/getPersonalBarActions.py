## Script (Python) "getPersonalBarActions"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=self=None
##title=
##
mapping = {'user': ['My Stuff', 'My Favorites', 'Preferences', 'Log out'] }
ordering = ['My Stuff', 'My Favorites', 'Preferences', 'Log out']

avail=None

personal_actions = {}

if self:
    avail = context.filter_actions(self, mapping)

if avail:
    for attr in ordering:
        if attr in avail.keys():
            personal_actions[attr]=avail[attr]
                
return personal_actions
