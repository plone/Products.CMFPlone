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
   Then anonymous users can register to the site

Scenario: Enable users to select their own passwords in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable users to select their own passwords
   Then users can select their own passwords when registering

Scenario: Enable user folders in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable user folders
   Then a user folder should be created when a user registers and logs in to the site

Scenario: Enable anyone to view 'about' information in the Security Control Panel
  Given a logged-in site administrator
    and a published test folder
    and the security control panel
   When I enable anyone to view 'about' information
   Then anonymous users can view 'about' information

Scenario: Enable use email as login in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable email to be used as a login name
   Then users can use email as their login name

Scenario: Enable use uuid as uid in the Security Control Panel
  Given a logged-in site administrator
    and the security control panel
   When I enable UUID to be used as a user id
   Then UUID should be used for the user id


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

the security control panel
  Go to  ${PLONE_URL}/@@security-controlpanel

a published test folder
  Go to  ${PLONE_URL}/robot-test-folder
  Click link  xpath=//li[@id='plone-contentmenu-workflow']/a
  Wait until element is visible  id=workflow-transition-publish
  Click link  id=workflow-transition-publish
  Wait until page contains  Item state changed

# --- WHEN -------------------------------------------------------------------

I enable self registration
  Select Checkbox  form.widgets.enable_self_reg:list
  Click Button  Save
  Wait until page contains  Changes saved

I enable users to select their own passwords
  Select Checkbox  form.widgets.enable_self_reg:list
  Select Checkbox  form.widgets.enable_user_pwd_choice:list
  Click Button  Save
  Wait until page contains  Changes saved

I enable user folders
  Select Checkbox  form.widgets.enable_self_reg:list
  Select Checkbox  form.widgets.enable_user_pwd_choice:list
  Select Checkbox  form.widgets.enable_user_folders:list
  Click Button  Save
  Wait until page contains  Changes saved

I enable anyone to view 'about' information
  Select Checkbox  form.widgets.allow_anon_views_about:list
  Click Button  Save
  Wait until page contains  Changes saved

I enable email to be used as a login name
  Select Checkbox  form.widgets.enable_self_reg:list
  Select Checkbox  form.widgets.enable_user_pwd_choice:list
  Select Checkbox  form.widgets.use_email_as_login:list
  Click Button  Save
  Wait until page contains  Changes saved

I enable UUID to be used as a user id
  Select Checkbox  form.widgets.enable_self_reg:list
  Select Checkbox  form.widgets.enable_user_pwd_choice:list
  Select Checkbox  form.widgets.use_uuid_as_userid:list
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

Anonymous users can register to the site
  Disable autologin
  Go to  ${PLONE_URL}
  Element Should Be Visible  xpath=//a[@id='personaltools-join']

Users can select their own passwords when registering
  Disable autologin
  Go to  ${PLONE_URL}/@@register
  Element Should Be Visible  xpath=//input[@id='form-widgets-password']

Users can use email as their login name
  Disable autologin
  Go to  ${PLONE_URL}/@@register
  Element Should Be Visible  xpath=//input[@id='form-widgets-email']
  Element Should Not Be Visible  xpath=//input[@id='form-widgets-username']

A user folder should be created when a user registers and logs in to the site

  Disable autologin

  # I register to the site
  Go to  ${PLONE_URL}/@@register
  Input Text  form.widgets.username  joe
  Input Text  form.widgets.email  joe@test.com
  Input Text  form.widgets.password  supersecret
  Input Text  form.widgets.password_ctl  supersecret
  Click Button  Register

  # I login to the site
  Go to  ${PLONE_URL}/login
  Input Text  __ac_name  joe
  Input Text  __ac_password  supersecret
  Click Button  Log in
  Wait until page contains  You are now logged in

  # The user folder should be created
  Go to  ${PLONE_URL}/Members/joe
  Element Should Contain  css=h1.documentFirstHeading  joe
  Page should Not contain  This page does not seem to exist

Anonymous users can view 'about' information
  Disable autologin
  Go to  ${PLONE_URL}/@@search?SearchableText=test
  Element Should Be Visible  xpath=//span[contains(@class, 'documentAuthor')]

UUID should be used for the user id

  Disable autologin

  # I register to the site
  Go to  ${PLONE_URL}/@@register
  Input Text  form.widgets.username  joe
  Input Text  form.widgets.email  joe@test.com
  Input Text  form.widgets.password  supersecret
  Input Text  form.widgets.password_ctl  supersecret
  Click Button  Register

  # I login to the site
  Go to  ${PLONE_URL}/login
  Input Text  __ac_name  joe
  Input Text  __ac_password  supersecret
  Click Button  Log in
  Wait until page contains  You are now logged in

  # XXX: Here we can't really test that this is a uuid, since it's random, so
  # we just check that user id is not equal to username or email
  ${userid}=  Get Text  xpath=//li[@id='portal-personaltools']//li[contains(@class, 'plone-toolbar-submenu-header')]//span
  Should Not Be Equal As Strings  ${userid}  joe
  Should Not Be Equal As Strings  ${userid}  joe@test.com
