*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run Keywords  Plone test setup
Test Teardown  Run keywords  Plone test teardown


*** Test Cases ***************************************************************

Scenario: Modify an existing action in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I modify an action title
   Sleep  1
   Then anonymous users can see the new action title

Scenario: Reorder in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I change the actions order
   Sleep  1
   Then anonymous users can see the actions new ordering

Scenario: Create a new action in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I add a new action
   Sleep  1
   Then logged-in users can see the new action

Scenario: Hide/show an action in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I hide an action
   Sleep  1
   Then anonymous users cannot see the action anymore
  Given a logged-in administrator
    and the actions control panel
   When I unhide the action
   Sleep  1
   Then anonymous users can see the action again

Scenario: Delete an action in Actions Control Panel
  Given a logged-in administrator
    and the actions control panel
   When I delete an action
   Sleep  1
   Then anonymous users cannot see the action anymore

*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in administrator
  Enable autologin as  Manager

the actions control panel
  Go to  ${PLONE_URL}/@@actions-controlpanel
  Wait until page contains  Portal actions

# --- WHEN -------------------------------------------------------------------

I modify an action title
  Click Link    css=section:nth-child(3) li:first-child a
  Wait until page contains  Action Settings
  Input Text for sure  form.widgets.title  A new site map
  Wait For Then Click Element  css=.pattern-modal-buttons > button

I change the actions order
  Click Link    css=section:nth-child(3) li:first-child a
  Wait until page contains  Action Settings
  Input Text for sure  form.widgets.position  3
  Wait For Then Click Element  css=.pattern-modal-buttons > button

I add a new action
  Click Link  Add new action
  Wait until page contains  New action
  Select From List By Label   form.widgets.category:list   User actions
  Input Text for sure  form.widgets.id  favorites
  Wait For Then Click Element  css=.pattern-modal-buttons > button
  Wait until page contains  favorites
  Wait For Then Click Element  css=section.category:last-child li:last-child a
  Wait until page contains  Action Settings
  Input Text for sure  form.widgets.title  My favorites
  Input Text for sure  form.widgets.url_expr  string:\${globals_view/navigationRootUrl}/favorites
  Wait For Then Click Element  css=.pattern-modal-buttons > button

I delete an action
  Click Button    css=section:nth-child(3) li:first-child button[name=delete]
  Handle alert

I hide an action
  Click Button    css=section:nth-child(3) li:first-child button[name=hide]

I unhide the action
  Click Button    css=section:nth-child(3) li:first-child button[name=show]

# --- THEN -------------------------------------------------------------------

anonymous users can see the new action title
  Disable autologin
  Go to  ${PLONE_URL}
  Wait until page contains  Accessibility
  Page Should Contain  A new site map

anonymous users can see the actions new ordering
  Disable autologin
  Go to  ${PLONE_URL}
  Wait until page contains  Accessibility
  Page Should Contain Element   xpath=//div[@id='portal-footer']//ul/li[1]/a/span[contains(text(), 'Accessibility')]
  Page Should Contain Element   xpath=//div[@id='portal-footer']//ul/li[3]/a/span[contains(text(), 'Site Map')]

logged-in users can see the new action
  Disable autologin
  Enable autologin as   Contributor
  Go to  ${PLONE_URL}
  Wait until page contains  Accessibility
  Page Should Contain  My favorites

anonymous users cannot see the action anymore
  Disable autologin
  Go to  ${PLONE_URL}
  Wait until page contains  Accessibility
  Page Should Not Contain  Site Map

anonymous users can see the action again
  Disable autologin
  Go to  ${PLONE_URL}
  Wait until page contains  Accessibility
  Page Should Contain  Site Map
