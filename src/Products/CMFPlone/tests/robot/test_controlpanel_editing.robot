*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot


Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown

*** Variables ***

${PAGE_TITLE}    Doc
${PAGE_ID}    doc

*** Test Cases ***

Scenario: Disable Standard Editor in the Editing Control Panel
    Given a logged-in site administrator
      and the editing control panel
     When I disable the standard editor
     Then I do not see the standard editor when I create a document

     When I go to the editing control panel
      and I enable the standard editor
     Then I see the standard editor when I create a document


Scenario: Enable Link Integrity Check in the Editing Control Panel
    Given a logged-in site administrator
      and the editing control panel
    When I enable link integrity checks
    # Linkintegrity checks are in `test_linkintegrity.robot`


Scenario: Enable Lock on Through The Web in the Editing Control Panel
    Given a logged-in site administrator
      and the editing control panel
      and a document '${PAGE_TITLE}'
     When I enable lock on through the web
      and I edit the document
     Then I will see a warning if a document is edited by another user


*** Keywords ***

# GIVEN

the editing control panel
    Go to    ${PLONE_URL}/@@editing-controlpanel


# WHEN

I disable the standard editor
    Select Options By    //select[@name="form.widgets.default_editor:list"]    label    None
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


I enable the standard editor
    Select Options By    //select[@name="form.widgets.default_editor:list"]    label    TinyMCE
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


I go to the editing control panel
    Go to    ${PLONE_URL}/@@editing-controlpanel


I enable link integrity checks
    Check Checkbox    //input[@name="form.widgets.enable_link_integrity_checks:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


I enable lock on through the web
    Check Checkbox    //input[@name="form.widgets.lock_on_ttw_edit:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I edit the document
    Go to    ${PLONE_URL}/${PAGE_ID}
    Click    //li[@id="contentview-edit"]/a
    Get Text    //body    contains    Edit Page


# THEN

I do not see the standard editor when I create a document
    Go To  ${PLONE_URL}/++add++Document
    Wait For Condition    Classes    //body    contains    patterns-loaded
    Wait For Condition    Element Count    //*[@id="formfield-form-widgets-IRichTextBehavior-text"]/div[@role="application"]    should be    0
    Wait For Condition    Element States    //textarea[@name="form.widgets.IRichTextBehavior.text"]    contains    visible


I see the standard editor when I create a document
    Go To  ${PLONE_URL}/++add++Document
    Wait For Condition    Classes    //body    contains    patterns-loaded
    Wait For Condition    Element Count    //*[@id="formfield-form-widgets-IRichTextBehavior-text"]/div[@role="application"]    should be    1
    Wait For Condition    Element States    //textarea[@name="form.widgets.IRichTextBehavior.text"]    contains    hidden

I will see a warning if a document is edited by another user
    Disable autologin
    Enable autologin as   Contributor    Reviewer    Manager
    New Page    ${PLONE_URL}/${PAGE_ID}
    Wait For Condition    Text    //body    contains    Lock
    Wait For Condition    Element Count    //input[@value="Unlock"]    should be    1
