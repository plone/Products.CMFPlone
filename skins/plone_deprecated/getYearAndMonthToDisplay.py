##parameters=
##title=Calendar Presentation Helper
context.plone_log("The getYearAndMonthToDisplay script is deprecated and will be "
                  "removed in plone 3.5.  Use the getYearAndMonthToDisplay method "
                  "of the @@calendar_view view instead.")

return context.restrictedTraverse('@@calendar_view').getYearAndMonthToDisplay()
