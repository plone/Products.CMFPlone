## Script (Python) "prepare_slots"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=generate a mapping based on the context slots
##
#prepare a structure that makes it conveient to determine
#if we want to use-macro or render the path expression.
#the values for the dictioanries is a list of tuples
#that are path expressions and the second value is a 
#1 for use-macro
#0 for render path expression

slots={ 'left':[],
        'right':[],
        'item_actions':[] }

for slot in [lslot for lslot in context.left_slots if lslot]:
    if slot.find('/macros/')!=-1:
        slots['left'].append( (slot, 1) )
    else:
        slots['left'].append( (slot, 0) )

for slot in [rslot for rslot in context.right_slots if rslot]:
    if slot.find('/macros/')!=-1:
        slots['right'].append( (slot, 1) )
    else:
        slots['right'].append( (slot, 0) )

for slot in [iaction for iaction in context.item_action_slots if iaction]:
    if slot.find('/macros/')!=-1:
        slots['item_actions'].append( (slot, 1) )
    else:
        slots['item_actions'].append( (slot, 0) )

return slots

