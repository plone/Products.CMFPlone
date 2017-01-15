*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test Cases ***************************************************************

Scenario: Social settings are provided
  Given a logged-in site administrator
    and the social control panel
   When I provide social settings
   Then social tags should exist

Scenario: Social tags are disabled
  Given a logged-in site administrator
    and the social control panel
   When I provide social settings
   When I disable social
   Then social tags should not exist


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the social control panel
  Go to  ${PLONE_URL}/@@social-controlpanel


# --- WHEN -------------------------------------------------------------------

I disable social
  UnSelect Checkbox  form.widgets.share_social_data:list
  Sleep  2
  Click Button  Save
  Wait until page contains  Changes saved

I provide social settings
  Input Text  name=form.widgets.twitter_username  plonecms
  Input Text  name=form.widgets.facebook_app_id  123456
  Input Text  name=form.widgets.facebook_username  plonecms
  Sleep  2
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

social tags should exist
  Go to  ${PLONE_URL}
  Page should contain element  css=meta[name="twitter:site"]
  Page should contain element  css=meta[property="og:article:publisher"]
  Page should contain element  css=meta[property="fb:app_id"]

social tags should not exist
  Go to  ${PLONE_URL}
  Page should not contain element  css=meta[name="twitter:site"]
  Page should not contain element  css=meta[property="og:article:publisher"]
  Page should not contain element  css=meta[property="fb:app_id"]
