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

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


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

Scenario: As a manager I can move user form fields
  Pass Execution  Drag and drop in schemaeditor does not work
  Given a logged-in manager
    and the mail setup configured
    and site registration enabled
   When I add a new text field to the member fields
    and choose to show the field in the user profile
    and I move the new field to the top
   Then a logged-in user will see the field on top of the user profile

Scenario: As a manager I can add a field with constraints to the registration form
  Given a logged-in manager
    and the mail setup configured
    and site registration enabled
   When I add a new text field to the member fields
    and choose to show the field in the user profile
    and add a min/max constraint to the field
   Then a logged-in user will see a field with min/max constraints



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
  Click Button  Add new field…
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
  Click Button  Add new field…
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

I move the new field to the top
  # XXX: Drag and drop is not working!!!
  Drag And Drop  xpath=//div[@data-field_id="test_field"]//span[contains(@class, "draghandle")]  xpath=//div[@data-field_id="home_page"]

add a min/max constraint to the field
  Click Link  xpath=//div[@data-field_id='test_field']//a[contains(@class, 'fieldSettings')]
  Wait until page contains element  form.widgets.min_length
  Input Text  form.widgets.min_length  4
  Input Text  form.widgets.max_length  6
  Click Button  css=.pattern-modal-buttons input#form-buttons-save
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

a logged-in user will see the field on top of the user profile
  a logged-in user will see the field in the user profile
  XPath Should Match X Times  //form[@id='form']/div[1]//input[@id='form-widgets-test_field']  1  message=test_field should be on top

a logged-in user will see a field with min/max constraints
  a logged-in user will see the field in the user profile
  Input Text  form.widgets.test_field  1
  Click Button  Save
  Wait until page contains  There were some errors.
  Page should contain  Value is too short
