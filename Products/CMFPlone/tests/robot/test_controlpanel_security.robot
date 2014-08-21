*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Enable self registration in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   I enable self registration
  Given an anonymous user
   When I go to the front page
   Then the registration link is shown in the page

Scenario: Enable users to select their own passwords in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   I enable self registration
   I enable users to select their own passwords
  Given an anonymous user
   I go to the registration form
   Then the password field is shown in the page

Scenario: Enable use email as login in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   I enable self registration
   I enable users to select their own passwords
   I enable use email as login
  Given an anonymous user
   I go to the registration form
   Then the email field is shown in the page
     and the username field is not shown in the page


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an anonymous user
  Disable autologin

the security control panel
  Go to  ${PLONE_URL}/@@security-controlpanel


# --- WHEN -------------------------------------------------------------------

I enable self registration
  Select Checkbox  form.widgets.enable_self_reg:list
  Click Button  Save
  Wait until page contains  Changes saved

I enable users to select their own passwords
  Select Checkbox  form.widgets.enable_user_pwd_choice:list
  Click Button  Save
  Wait until page contains  Changes saved

I enable use email as login
  Select Checkbox  form.widgets.use_email_as_login:list
  Click Button  Save
  Wait until page contains  Changes saved

I go to the front page
  Go to  ${PLONE_URL}

I go to the registration form
  Go to  ${PLONE_URL}/@@register


# --- THEN -------------------------------------------------------------------

The registration link is shown in the page
  Element Should Be Visible  xpath=//a[@id='personaltools-join']

The password field is shown in the page
  Element Should Be Visible  xpath=//input[@id='form-widgets-password']

The email field is shown in the page
  Element Should Be Visible  xpath=//input[@id='form-widgets-email']

The username field is not shown in the page
  Element Should Not Be Visible  xpath=//input[@id='form-widgets-username']
