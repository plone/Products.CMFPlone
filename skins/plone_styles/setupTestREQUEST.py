## Script (Python) "setupTestREQUEST"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=setups a faux REQUEST for alex to test
##
REQUEST=context.REQUEST

# if this is here, I can checkin via SF :)


# Main
REQUEST.set('mainFont', '10px Verdana, Helvetica, Arial, sans-serif')
REQUEST.set('mainBackground', 'White')
REQUEST.set('mainTextColor', 'Black')
REQUEST.set('mainLinkColor', '#436976')

# Main tabs
REQUEST.set('mainTabBorder', '1px solid #8CACBB')
REQUEST.set('mainTabBackground', '#DEE7EC')
REQUEST.set('mainTabBackgroundNotSelected', 'transparent')
REQUEST.set('mainTabBackdrop', 'transparent')
REQUEST.set('mainTabLinkColor', '#436976')

# Headlines
REQUEST.set('headingFont', '10px normal')
REQUEST.set('headingSize1', '240%')
REQUEST.set('headingSize2', '200%')
REQUEST.set('headingSize3', '160%')
REQUEST.set('headingSize4', '140%')
REQUEST.set('headingSize5', '120%')
REQUEST.set('headingSize6', '110%')

# Description
REQUEST.set('descriptionFont', 'bold 120% Verdana, Helvetica, Arial, sans-serif')

# Content
REQUEST.set('contentFont', '120%')
REQUEST.set('contentBackground', 'dummy')
REQUEST.set('contentImageBorder', '1px solid black')
# add contentLinkVisited etc? Yes!

# Content Tabs
REQUEST.set('contentTabBorder', '1px solid #74AE0B')
REQUEST.set('contentTabBackground', '#CDE2A7')
REQUEST.set('contentTabBackgroundNotSelected', 'transparent')
REQUEST.set('contentTabBackdrop', 'dummy')
REQUEST.set('contentTabLinkColor', '#578308')


# Pre
REQUEST.set('preBorder', '1px solid #8cacbb')
REQUEST.set('preBackground', '#dee7ec')


# Messages
REQUEST.set('messageFont', 'bold')
REQUEST.set('messageBackground', '#FFCE7B')
REQUEST.set('messageBorder', '1px solid #FFA500')

# Special
REQUEST.set('textTransform', 'dummy')
REQUEST.set('noBorder', 'none') # should be 1px solid #8cacbb in Mozilla
REQUEST.set('evenRowBackground', '#F7F9FA')
REQUEST.set('oddRowBackground', 'transparent')
REQUEST.set('groupBorder', '1px solid #8cacbb')
REQUEST.set('requiredField', 'url(plone_images/required.gif) 1em no-repeat')

# Input gadgets 
REQUEST.set('inputFont', 'bold 10px Verdana, Helvetica, Arial, sans-serif')
REQUEST.set('inputBorder', '1px solid #8cacbb')

# Buttons
REQUEST.set('contextButtonBackground', 'transparent url(plone_images/linkTransparent.gif) left no-repeat')
REQUEST.set('contextButtonPadding', '1px 1px 1px 15px')
REQUEST.set('standaloneButtonBackground', '#DEE7EC url(plone_images/linkOpaque.gif) left no-repeat')
REQUEST.set('standaloneButtonPadding', '1px 1px 1px 15px')





# Top 
REQUEST.set('topBackground', 'transparent')
REQUEST.set('topMargin', '0')
REQUEST.set('topPadding', '0')

REQUEST.set('logoMargin', '0')
REQUEST.set('logoPadding', '1em 0em 1em 2em')

REQUEST.set('searchMargin', '3em 0em 0em 0em')
REQUEST.set('searchPadding', '0em 2em 0em 0em')

# Footer
REQUEST.set('footerBackground', '#DEE7EC')
REQUEST.set('footerBorder', '1px solid #8CACBB')

# Columns
REQUEST.set('leftColumnWidth', '14%')
REQUEST.set('mainColumnWidth', '72%')
REQUEST.set('rightColumnWidth', '14%')

