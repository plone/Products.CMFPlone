*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Change Default Markup Types in the Markup Control Panel
  Given a logged-in site administrator
    and the markup control panel
   When I set allowed types to "text/restructured"
#TODO: Waiting on richtext pattern to support this
#   Then I do not see the standard editor when I create a document

Scenario: Set Default Markup to be Restructured Text
  Given a logged-in site administrator
    and the markup control panel
   When I set the default type to "text/restructured"
#TODO: Waiting on richtext pattern to support this
#   Then I do not see the standard editor when I create a document


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a document '${title}'
  Create content  type=Document  id=doc  title=${title}

the markup control panel
  Go to  ${PLONE_URL}/@@markup-controlpanel


# --- WHEN -------------------------------------------------------------------

I set allowed types to "${type}"
  with the label  text/html  UnSelect Checkbox
  with the label  text/x-web-textile  UnSelect Checkbox
  with the label  ${type}   Select Checkbox
  Click Button  Save
  Wait until page contains  Changes saved

I set the default type to "${type}"
  With the label  Default format  select from list  ${type}
  Click Button  Save
  Wait until page contains  Changes saved



# --- THEN -------------------------------------------------------------------

Then I can see only "${type}" when creating a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  with the label  Title   Input Text    My Document
  Click Link  Settings
  Page should contain element  name=form.widgets.IShortName.id
  Input Text  name=form.widgets.IShortName.id  this-is-my-custom-short-name
  Click Button  Save
  Wait until page contains  Item created
  Location should be  ${PLONE_URL}/this-is-my-custom-short-name/view

I do not see the standard editor when I create a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  Page should not contain element  css=.mce-tinymce

# --- Helpers -----------------------------------------------------------------

With the label
    [arguments]  ${title}    ${extra_keyword}   @{list}
    ${for}=  label "${title}"
    Run Keyword     ${extra_keyword}  id=${for}   @{list}

label "${title}"
    [Return]  ${for}
    ${for}=  Get Element Attribute  xpath=//label[contains(., "${title}")]@for

label2 "${title}"
    [Return]  ${for}
    ${for}=  Get Element Attribute  xpath=//label[contains(., "${title}")]//input
