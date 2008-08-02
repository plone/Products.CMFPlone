## Script (Python) "cropText"
##parameters=text, length, ellipsis='...'
##title=Crop text on a word boundary

context.plone_log("The cropText script is deprecated and will be "
                  "removed in Plone 4.0. Use the cropText method "
                  "of the @@plone view instead.")

return context.restrictedTraverse('@@plone').cropText(text, length, ellipsis='...')
