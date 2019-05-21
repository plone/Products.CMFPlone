*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Set Site Language in the Language Control Panel
  Given a logged-in site administrator
    and the language control panel
   When I set the site language to German
   Then the Plone user interface is in German


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the language control panel
  Go to  ${PLONE_URL}/@@language-controlpanel
  Wait until page contains  Language Settings


# --- WHEN -------------------------------------------------------------------

I set the site language to German
  Select From List By Label  form.widgets.default_language:list  Deutsch
  Select From List By Label  form.widgets.available_languages.from  Deutsch
  Click Button  →
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

the Plone user interface is in German
  Go to  ${PLONE_URL}
  Wait until page contains  Sie sind hier
  Page should contain  Sie sind hier
