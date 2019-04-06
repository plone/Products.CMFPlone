*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Disable Generate Tabs in the Navigation Control Panel
  Given a logged-in site administrator
    and a document 'My Document'
    and the navigation control panel
   When I disable generate tabs
   Then the document 'My Document' does not show up in the navigation

Scenario: Enable Folderish Tabs in the Navigation Control Panel
  Given a logged-in site administrator
    and a document 'My Document'
    and the navigation control panel
   When I disable non-folderish tabs
   Then the document 'My Document' does not show up in the navigation

Scenario: Filter Navigation By Displayed Types in the Navigation Control Panel
  Given a logged-in site administrator
    and a document 'My Document'
    and the navigation control panel
   When I remove 'Document' from the displayed types list
   Then the document 'My Document' does not show up in the navigation
    and the document 'My Document' does not show up in the sitemap

#Scenario: Filter Navigation By Workflow States in the Navigation Control Panel
#  Given a logged-in site administrator
#    and a published document 'My Document'
#    and a private document 'My Internal Document'
#    and the navigation control panel
#   When I enable filtering by workflow states
#    and I choose to show 'published' items
#    and I choose to not show 'private' items
#   Then the document 'My Document' shows up in the navigation
#    and the document 'My Internal Document' does not show up in the navigation


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

the navigation control panel
  Go to  ${PLONE_URL}/@@navigation-controlpanel
  Wait until page contains  Navigation Settings

a published document '${title}'
  ${uid}=  a document '${title}'
  Fire transition  ${uid}  publish

a private document '${title}'
  a document '${title}'


# --- WHEN -------------------------------------------------------------------

I disable generate tabs
  Unselect Checkbox  form.widgets.generate_tabs:list
  Click Button  Save
  Wait until page contains  Changes saved

I disable non-folderish tabs
  Unselect Checkbox  xpath=//input[@value='Document']
  Click Button  Save
  Wait until page contains  Changes saved

I remove '${portal_type}' from the displayed types list
  Unselect Checkbox  xpath=//input[@value='Document']
  Click Button  Save
  Wait until page contains  Changes saved

I enable filtering by workflow states
  Select Checkbox  name=form.widgets.filter_on_workflow:list
  Click Button  Save
  Wait until page contains  Changes saved

I choose to show '${workflow_state}' items
  Select Checkbox  xpath=//input[@value='${workflow_state}']
  Click Button  Save
  Wait until page contains  Changes saved

I choose to not show '${workflow_state}' items
  Unselect Checkbox  xpath=//input[@value='${workflow_state}']
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

the document '${title}' shows up in the navigation
  Go to  ${PLONE_URL}
  Wait until page contains  Powered by Plone
  XPath Should Match X Times  //ul[@id='portal-globalnav']/li/a[contains(text(), '${title}')]  1  message=The global navigation should have contained the item '${title}'

the document '${title}' does not show up in the navigation
  Go to  ${PLONE_URL}
  Wait until page contains  Powered by Plone
  XPath Should Match X Times  //ul[@id='portal-globalnav']/li/a[contains(text(), '${title}')]  0  message=The global navigation should not have contained the item '${title}'

the document '${title}' does not show up in the sitemap
  Go to  ${PLONE_URL}/sitemap
  Wait until page contains  Powered by Plone
  XPath Should Match X Times  //ul[@id='portal-sitemap']/li/a/span[contains(text(), '${title}')]  0  message=The sitemap should not have contained the item '${title}'
