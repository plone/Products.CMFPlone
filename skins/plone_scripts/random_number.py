## Script (Python) "random_number"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

import random
from DateTime import DateTime

num = str(DateTime().millis()) + str(random.randint(0, 1000000))
return num

