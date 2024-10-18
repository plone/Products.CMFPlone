*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: Change Default Markup Types in the Markup Control Panel
    Given a logged-in site administrator
      and the markup control panel
     When I set allowed types to    text/restructured

    #TODO: Waiting on richtext pattern to support this
    #Then I do not see the standard editor when I create a document

Scenario: Set Default Markup to be Restructured Text
    Given a logged-in manager
      and the markup control panel
     When I set the default type to    text/restructured

    #TODO: Waiting on richtext pattern to support this
    #Then I do not see the standard editor when I create a document

*** Keywords ***

# GIVEN

the markup control panel
    Go to    ${PLONE_URL}/@@markup-controlpanel
    Get Text    //body    contains    Markup Settings


# --- WHEN -------------------------------------------------------------------

I set allowed types to
    [Arguments]    ${type}

    Check Checkbox    //input[@name="form.widgets.allowed_types:list" and @value="${type}"]
    Uncheck Checkbox    //input[@name="form.widgets.allowed_types:list" and @value="text/html"]
    Uncheck Checkbox    //input[@name="form.widgets.allowed_types:list" and @value="text/x-web-textile"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

    Get Element States    //input[@name="form.widgets.allowed_types:list" and @value="${type}"]    contains    checked
    Get Element States    //input[@name="form.widgets.allowed_types:list" and @value="text/html"]    not contains    checked
    Get Element States    //input[@name="form.widgets.allowed_types:list" and @value="text/x-web-textile"]    not contains    checked

I set the default type to
    [Arguments]    ${type}

    Select Options By    //select[@name="form.widgets.default_type:list"]    value    ${type}
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.

# I disable the standard editor
#   Select from list by label  name=form.widgets.default_editor:list  None
#   Click Button  Save
#   Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

Then I can see only "${type}" when creating a document
  Go To  ${PLONE_URL}/++add++Document
  Wait until page contains  Add Page
  with the label  Title   Input Text    My Document
  Click Link  Settings
  Page should contain element  name=form.widgets.IShortName.id
  Input Text  name=form.widgets.IShortName.id  this-is-my-custom-short-name
  Click Button  Save
  Wait until page contains  Item created
  Location should be  ${PLONE_URL}/this-is-my-custom-short-name/view

# I do not see the standard editor when I create a document
#     Go To  ${PLONE_URL}/++add++Document
#     Pause
#     Page should not contain element  css=.mce-tinymce
