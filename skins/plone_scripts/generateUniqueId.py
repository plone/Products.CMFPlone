## Script (Python) "generateUniqueId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=type_name=None
##title=
##
from DateTime import DateTime
from random import random

now=DateTime()
prefix=''
suffix=''

if type_name is not None:
    prefix = type_name.replace(' ', '_')+'.'

id=now.strftime('%Y-%m-%d')+'.'+str(now.millis())[5:]+str(random())[2:4]
return prefix+id+suffix
