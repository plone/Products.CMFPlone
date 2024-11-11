*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: When page is linked show warning
  Given a logged-in site administrator
    and a page to link to
    and a page to edit
   When I add a link in rich text
   Then I should see a warning when deleting page

Scenario: After you fix linked page no longer show warning
  Given a logged-in site administrator
    and a page to link to
    and a page to edit
   When I add a link in rich text
   Then I should see a warning when deleting page

   When I remove link to page
   Then I should not see a warning when deleting page

Scenario: Show warning when deleting linked item from folder_contents
    Given a logged-in site administrator
      and a page to link to
      and a page to edit
     When I add a link in rich text
     Then I should see a warning when deleting page from folder_contents

     When I remove link to page
     Then I should not see a warning when deleting page from folder_contents

*** Keywords ***

# GIVEN

a page to link to
    Create content
    ...    type=Document
    ...    id=foo
    ...    title=Foo

a page to edit
    Create content
    ...    type=Document
    ...    id=bar
    ...    title=Bar

# When
I add a link in rich text
    Go To    ${PLONE_URL}/bar/edit
    Fill text to tinymce editor    foo
    Mark text foo in tinymce editor
    Click    //button[@aria-label="Insert/edit link"]
    Wait For Condition    Element States    //div[@class="modal-content"]    contains    visible
    Click    //div[@class="modal-body"]//fieldset[@data-linktype="internal"]//button[contains(@class,"mode") and contains(@class,"browse")]
    Click    //a[@title="Go one level up"]
    Click    //a[contains(@class,"selectable") and @data-path="/foo"]
    Click    //div[contains(@class,"modal-footer")]//input[@name="insert"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I remove link to page
    Go To    ${PLONE_URL}/bar
    Click    //*[@id="contentview-edit"]//a
    Fill text to tinymce editor    foo
    Mark text foo in tinymce editor
    Click    //button[@aria-label="Remove link"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

# Then

I should see a warning when deleting page
    Go To  ${PLONE_URL}/foo
    Click    //*[@id="plone-contentmenu-actions"]/a
    Click    //*[@id="plone-contentmenu-actions-delete"]
    Get Element Count    //*[contains(@class,"breach-container")]//*[contains(@class,"breach-item")]    greater than    0

I should not see a warning when deleting page
    Go To  ${PLONE_URL}/foo
    Click    //*[@id="plone-contentmenu-actions"]/a
    Click    //*[@id="plone-contentmenu-actions-delete"]
    Get Element Count    //*[contains(@class,"breach-container")]//*[contains(@class,"breach-item")]    should be    0


I should see a warning when deleting page from folder_contents
    Go To  ${PLONE_URL}/folder_contents
    Check Checkbox    //tr[@data-id="foo"]//input
    Get Checkbox State      //tr[@data-id="foo"]//input    ==    checked
    Get Element Count    //*[@id="btngroup-mainbuttons"]//a[@id="btn-delete" and contains(@class,"disabled")]    should be    0
    Click    //*[@id="btngroup-mainbuttons"]//a[@id="btn-delete"]
    Get Element Count    //*[contains(@class,"breach-container")]//*[contains(@class,"breach-item")]    greater than    0
    Get Checkbox State      //tr[@data-id="foo"]//input    ==    checked


I should not see a warning when deleting page from folder_contents
    Go To  ${PLONE_URL}/folder_contents
    Check Checkbox    //tr[@data-id="foo"]//input
    Get Checkbox State      //tr[@data-id="foo"]//input    ==    checked
    Get Element Count    //*[@id="btngroup-mainbuttons"]//a[@id="btn-delete" and contains(@class,"disabled")]    should be    0
    Click    //*[@id="btngroup-mainbuttons"]//a[@id="btn-delete"]
    Get Element States    //*[@id="popover-delete"]//*[contains(@class,"popover-content")]    contains    visible
    Get Element Count    //*[contains(@class,"breach-container")]//*[contains(@class,"breach-item")]    should be    0
    Click    //*[contains(@class,"popover-content")]//button[contains(@class,"applyBtn")]
    Get Text    //body    contains    Successfully delete items
    Get Element Count      //tr[@data-id="foo"]//input    should be    0

# DRY

Mark text foo in tinymce editor

    # select the text `heading` via javascript
    Evaluate JavaScript    ${None}
    ...    () => {
    ...        let iframe_document = document.querySelector(".tox-edit-area iframe").contentDocument;
    ...        let body = iframe_document.body;
    ...        let p = body.firstChild;
    ...        let range = new Range();
    ...        range.setStart(p.firstChild, 0);
    ...        range.setEnd(p.firstChild, 3);
    ...        iframe_document.getSelection().removeAllRanges();
    ...        iframe_document.getSelection().addRange(range);
    ...    }
    ...    all_elements=False
