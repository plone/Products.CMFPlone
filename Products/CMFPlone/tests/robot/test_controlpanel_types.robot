*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************
Scenario: Change default workflow
  Given a logged-in site administrator
    and the types control panel
   When I select 'Single State Workflow' workflow
   Then Wait until page contains  Content Settings
   When I add new Link 'my_link'
    Then Link 'my_link' should have Single State Workflow enabled


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------
the types control panel
  Go to  ${PLONE_URL}/@@content-controlpanel
  Wait until page contains  Content Settings


# --- WHEN -------------------------------------------------------------------
I select '${workflow}' workflow
  Select from list by label  name=new_workflow  ${workflow}
  Click Button  Save

I add new Link '${id}'
  Go to  ${PLONE_URL}
  Wait until page contains  Plone site
  Create content  type=Link  id=${id}  title=${id}  remoteUrl=http://www.starzel.de


# --- THEN -------------------------------------------------------------------

Link '${id}' should have Single State Workflow enabled
  Go to  ${PLONE_URL}/${id}
  Wait until page contains  ${id}
  # We check that single state worklow is used, publish button is not present
  Page should not contain element  xpath=//a[@id="workflow-transition-publish"]
