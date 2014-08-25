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
   When I enable self registration
    and I save the settings
  Given an anonymous user
    and the front page
   Then the registration link is shown in the page

Scenario: Enable users to select their own passwords in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable self registration
    and I enable users to select their own passwords
    and I save the settings
  Given an anonymous user
    and the registration form
   Then the password field is shown in the page

Scenario: Enable user folders in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable self registration
    and I enable users to select their own passwords
    and I enable user folders
    and I save the settings
  Given an anonymous user
   When I register to the site
    and I login to the site
   Then the user folder should be created

Scenario: Enable use email as login in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable self registration
    and I enable users to select their own passwords
    and I enable use email as login
    and I save the settings
  Given an anonymous user
    and the registration form
   Then the email field is shown in the page
     and the username field is not shown in the page

Scenario: Enable use uuid as uid in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable self registration
    and I enable users to select their own passwords
    and I enable uuid as user id
    and I save the settings
  Given an anonymous user
   When I register to the site
    and I login to the site
   Then uuid should be used for user id


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an anonymous user
  Disable autologin

the security control panel
  Go to  ${PLONE_URL}/@@security-controlpanel

the registration form
  Go to  ${PLONE_URL}/@@register

the front page
  Go to  ${PLONE_URL}

# --- WHEN -------------------------------------------------------------------

I enable self registration
  Select Checkbox  form.widgets.enable_self_reg:list

I enable users to select their own passwords
  Select Checkbox  form.widgets.enable_user_pwd_choice:list

I enable use email as login
  Select Checkbox  form.widgets.use_email_as_login:list

I enable user folders
  Select Checkbox  form.widgets.enable_user_folders:list

I enable uuid as user id
  Select Checkbox  form.widgets.use_uuid_as_userid:list

I save the settings
  Click Button  Save
  Wait until page contains  Changes saved

I register to the site
  Go to  ${PLONE_URL}/@@register
  Input Text  form.widgets.username  joe
  Input Text  form.widgets.email  joe@test.com
  Input Text  form.widgets.password  supersecret
  Input Text  form.widgets.password_ctl  supersecret
  Click Button  Register

I login to the site
  Go to  ${PLONE_URL}/login
  Input Text  __ac_name  joe
  Input Text  __ac_password  supersecret
  Click Button  Log in
  Wait until page contains  You are now logged in


# --- THEN -------------------------------------------------------------------

The registration link is shown in the page
  Element Should Be Visible  xpath=//a[@id='personaltools-join']

The password field is shown in the page
  Element Should Be Visible  xpath=//input[@id='form-widgets-password']

The email field is shown in the page
  Element Should Be Visible  xpath=//input[@id='form-widgets-email']

The username field is not shown in the page
  Element Should Not Be Visible  xpath=//input[@id='form-widgets-username']

The user folder should be created
  Go to  ${PLONE_URL}/Members/joe
  Element Should Contain  css=h1.documentFirstHeading  joe
  Page should Not contain  This page does not seem to exist

# XXX: Here we can't really test that this is a uuid, since it's random, so
# we just check that user id is not equal to username or email
uuid should be used for user id
  ${userid}=  Get Text  user-name
  Should Not Be Equal As Strings  ${userid}  joe
  Should Not Be Equal As Strings  ${userid}  joe@test.com
