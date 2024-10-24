*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

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



*** Keywords ***

# GIVEN

site registration enabled
    Go To  ${PLONE_URL}/@@security-controlpanel
    Get Text    //body    contains    Security Settings
    Check Checkbox    //input[@name="form.widgets.enable_self_reg:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

# WHEN

I add a new text field to the member fields
    Go to    ${PLONE_URL}/@@member-fields
    Click    //a[@id="add-field"]
    Type Text    //form[@id="add-field-form"]//input[@name="form.widgets.title"]    Test Field
    Press Keys  //form[@id="add-field-form"]//input[@name="form.widgets.title"]    Tab
    Select Options By    //form[@id="add-field-form"]//select[@name="form.widgets.factory:list"]    label    Text line (String)
    Click    //div[@class="modal-footer"]//button[@name="form.buttons.add"]
    Get Text    //body    contains    Field added successfully.

I Open the test_field Settings
    Go to    ${PLONE_URL}/@@member-fields
    Click    //div[@data-field_id="test_field"]//a[contains(@class,"fieldSettings")]

I add a new required text field to the member fields
    Go to  ${PLONE_URL}/@@member-fields
    Click    //a[@id="add-field"]
    Type Text    //form[@id="add-field-form"]//input[@name="form.widgets.title"]    Test Field
    Press Keys  //form[@id="add-field-form"]//input[@name="form.widgets.title"]    Tab
    Select Options By    //form[@id="add-field-form"]//select[@name="form.widgets.factory:list"]    label    Text line (String)
    Check Checkbox    //input[@name="form.widgets.required:list"]
    Click    //div[@class="modal-footer"]//button[@name="form.buttons.add"]
    Get Text    //body    contains    Field added successfully.

choose to show the field on registration
    I Open the test_field Settings
    Check Checkbox  //input[@name="form.widgets.IUserFormSelection.forms:list" and @value="On Registration"]
    Click    //div[@class="modal-footer"]//button[@name="form.buttons.save"]
    Get Text    //body    contains    Data successfully updated.

choose to show the field in the user profile
    I Open the test_field Settings
    Check Checkbox  //input[@name="form.widgets.IUserFormSelection.forms:list" and @value="In User Profile"]
    Click    //div[@class="modal-footer"]//button[@name="form.buttons.save"]
    Get Text    //body    contains    Data successfully updated.

I move the new field to the top
    Drag And Drop    //div[@data-field_id="test_field"]//span[contains(@class, "draghandle")]    //div[@data-field_id="home_page"]


add a min/max constraint to the field
    I Open the test_field Settings
    Type Text    //input[@name="form.widgets.min_length"]    4
    Type Text    //input[@name="form.widgets.max_length"]    6
    Click    //div[@class="modal-footer"]//button[@name="form.buttons.save"]
    Get Text    //body    contains    Data successfully updated.


# THEN

an anonymous user will see the field in the registration form
    Disable Autologin
    Go to    ${PLONE_URL}/@@register
    Get Text    //body    contains    Register
    Get Element Count    //input[@name="form.widgets.test_field"]    should be    1

a logged-in user will see the field in the user profile
    Disable Autologin
    a logged-in member
    Go to    ${PLONE_URL}/@@personal-information
    Get Element Count    //input[@name="form.widgets.test_field"]    should be    1

a logged-in user will see the required field in the user profile
    a logged-in user will see the field in the user profile
    Get Element Count    //div[@id='formfield-form-widgets-test_field']//span[contains(@class, 'required')]    should be    1    message=test_field should be required

a logged-in user will see the field on top of the user profile
    a logged-in user will see the field in the user profile
    Get Element Count    //form[@id='form']/div[1]//input[@id='form-widgets-test_field']    should be    1    message=test_field should be on top

a logged-in user will see a field with min/max constraints
    a logged-in user will see the field in the user profile
    Type Text    //input[@name="form.widgets.email"]    test@plone.org
    Type Text    //input[@name="form.widgets.test_field"]    1
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    There were some errors.
    Get Text    //body    contains    Value is too short
