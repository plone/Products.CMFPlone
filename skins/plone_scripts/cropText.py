## Script (Python) "cropText"
##parameters=text, length, ellipsis='...'
##title=Crop text on a word boundary
from Products.CMFCore.utils import getToolByName

converted = False
if not same_type(text, u''):
    putils = getToolByName(context, 'plone_utils')
    encoding = putils.getSiteEncoding()
    text = text.decode(encoding)
    converted = True
   
if len(text)>length:
    text = text[:length]
    l = text.rfind(' ')
    if l > length/2:
        text = text[:l+1]
    text += ellipsis
    
if converted:
    text = text.encode(encoding)
return text
