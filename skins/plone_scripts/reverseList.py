## Script (Python) "reverseList.py $Revision: 1.1.1.2 $"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=aList
##title=Reverse A List or Tuple and Return it
##

myList=[]

try:
    myList=list(aList)[:]
    myList.reverse()
except TypeError:
    pass

return myList
