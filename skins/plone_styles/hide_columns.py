## Script (Python) "hide_columns"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sl,sr
##title=
##

column_left=sl
column_right=sr

if column_right==[] and column_left==[]:
    return "hideboth"
if column_right!=[]and column_left==[]:
    return "hideleft"
if column_right==[]and column_left!=[]:
    return "hideright"
return "hidenone"
