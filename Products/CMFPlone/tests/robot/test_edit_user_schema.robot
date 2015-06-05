# ============================================================================
# Tests Editing the User Schema
# ============================================================================
#
# $ bin/robot-server --reload-path src/Products.CMFPlone/Products/CMFPlone/ Products.CMFPlone.testing.PRODUCTS_CMFPLONE_ROBOT_TESTING
#
# $ bin/robot src/Products.CMFPlone/Products/CMFPlone/tests/robot/test_edit_user_schema.robot
#
# ============================================================================

*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a manager I can add a field to the registration form
  Given a logged-in manager
    and the mail setup configured
    and site registration enabled
   When I add a new text field to the member fields
    and choose to show the field on registration
   Then an anonymous user will see the field in the registration form

Scenario: As a manager I can add a field to the user form
  Given a logged-in manager
    and the mail setup configured
    and site registration enabled
   When I add a new text field to the member fields
    and choose to show the field in the user profile
   Then a logged-in user will see the field in the user profile

Scenario: As a manager I can add a required field to the user form
  Given a logged-in manager
    and the mail setup configured
    and site registration enabled
   When I add a new required text field to the member fields
    and choose to show the field in the user profile
   Then a logged-in user will see the required field in the user profile


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

a logged-in manager
  Enable autologin as  Manager

site registration enabled
  Go To  ${PLONE_URL}/@@security-controlpanel
  Wait until page contains element  form.widgets.enable_self_reg:list
  Select Checkbox  form.widgets.enable_self_reg:list
  Click Button  Save
  Wait until page contains  Changes saved.


# --- WHEN -------------------------------------------------------------------

I add a new text field to the member fields
  Go to  ${PLONE_URL}/@@member-fields
  Wait until page contains element  css=#add-field
  Click link   css=#add-field
  Wait Until Element Is visible  css=#add-field-form #form-widgets-title
  Input Text  css=#add-field-form #form-widgets-title  test_field
  Input Text  css=#add-field-form #form-widgets-__name__  test_field
  Select From List  css=#form-widgets-factory  Text line (String)
  Click button  css=.pattern-modal-buttons input#form-buttons-add
  # XXX: This is really really bad! We need a UI notification like:
  # Wait until page contains  Field created.
  Sleep  1

I add a new required text field to the member fields
  Go to  ${PLONE_URL}/@@member-fields
  Wait until page contains element  css=#add-field
  Click link   css=#add-field
  Wait Until Element Is visible  css=#add-field-form #form-widgets-title
  Input Text  css=#add-field-form #form-widgets-title  test_field
  Input Text  css=#add-field-form #form-widgets-__name__  test_field
  Select From List  css=#form-widgets-factory  Text line (String)
  Select Checkbox  form.widgets.required:list
  Click button  css=.pattern-modal-buttons input#form-buttons-add
  # XXX: This is really really bad! We need a UI notification like:
  # Wait until page contains  Field created.
  Sleep  1

choose to show the field on registration
  Go to  ${PLONE_URL}/@@member-fields
  Wait until page contains element  css=div[data-field_id='test_field']
  Click link  css=div[data-field_id='test_field'] a.fieldSettings
  Wait Until Element Is visible  form.widgets.IUserFormSelection.forms:list
  Select Checkbox  css=#form-widgets-IUserFormSelection-forms-0
  Click button  css=.pattern-modal-buttons input#form-buttons-save
  # XXX: This is really really bad! We need a UI notification like:
  # Wait until page contains  Field created.
  Sleep  1

choose to show the field in the user profile
  Go to  ${PLONE_URL}/@@member-fields
  Wait until page contains element  css=div[data-field_id='test_field']
  Click link  css=div[data-field_id='test_field'] a.fieldSettings
  Wait Until Element Is visible  form.widgets.IUserFormSelection.forms:list
  Select Checkbox  css=#form-widgets-IUserFormSelection-forms-1
  Click button  css=.pattern-modal-buttons input#form-buttons-save
  # XXX: This is really really bad! We need a UI notification like:
  # Wait until page contains  Field created.
  Sleep  1


# --- THEN -------------------------------------------------------------------

an anonymous user will see the field in the registration form
  Disable Autologin
  Go to  ${PLONE_URL}/@@register
  Wait until page contains  Register
  Page should contain element  form.widgets.test_field

a logged-in user will see the field in the user profile
  Disable Autologin
  Enable autologin as  Member
  Go to  ${PLONE_URL}/@@personal-information
  Wait until page contains  Change your personal information
  Page should contain element  form.widgets.test_field

a logged-in user will see the required field in the user profile
  a logged-in user will see the field in the user profile
  XPath Should Match X Times  //div[@id='formfield-form-widgets-test_field']//span[contains(@class, 'required')]  1  message=test_field should be required
