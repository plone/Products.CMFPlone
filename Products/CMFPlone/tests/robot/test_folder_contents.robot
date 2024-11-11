*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test cases ***


Scenario: Select All items
    Given a logged-in site administrator
      and a folder with four pages
      and the folder contents view
     When I select all the elements
     Then the selection count appears
      and the clear selection link appears

    When I clear the selection
    Then no elements should be selected

Scenario: Reorder Folder Contents
   Given a logged-in site administrator
     and a folder with four pages
     and the folder contents view
    Then The Order Should Be    1    2    3    4
    When I reorder the elements
    Then The Order Should Be    4    3    2    1


*** Keywords ***


a folder with four pages
    ${folder_uid}=    Create content
    ...    type=Folder
    ...    title=My Folder
    Create content
    ...    type=Document
    ...    title=Doc1
    ...    container=${folder_uid}
    Create content
    ...    type=Document
    ...    title=Doc2
    ...    container=${folder_uid}
    Create content
    ...    type=Document
    ...    title=Doc3
    ...    container=${folder_uid}
    Create content
    ...    type=Document
    ...    title=Doc4
    ...    container=${folder_uid}

the folder contents view
    Go to    ${PLONE_URL}/my-folder/folder_contents

I click the '${link_name}' link
    Click    //a[contains(text(),${link_name})]

I select all the elements
    Wait For Condition    Classes    //body    contains    patterns-loaded
    Check Checkbox    //tr[@data-id="doc1"]//input[@type="checkbox"]
    Wait For Elements State     //tr[@data-id="doc1"]//input[@type="checkbox"]    checked    timeout=10s
    Check Checkbox    //tr[@data-id="doc2"]//input[@type="checkbox"]
    Wait For Elements State     //tr[@data-id="doc2"]//input[@type="checkbox"]    checked    timeout=10s
    Check Checkbox    //tr[@data-id="doc3"]//input[@type="checkbox"]
    Wait For Elements State     //tr[@data-id="doc3"]//input[@type="checkbox"]    checked    timeout=10s
    Check Checkbox    //tr[@data-id="doc4"]//input[@type="checkbox"]
    Wait For Elements State     //tr[@data-id="doc4"]//input[@type="checkbox"]    checked    timeout=10s

the selection count appears
    Get Text    //*[@id="btn-selected-items"]//*[contains(@class,"label-success")]    should be    4

the clear selection link appears
    Get Element Count    //a[contains(@class,"remove-all")]    greater than    0

I clear the selection
    Wait For Condition    Classes    //body    contains    patterns-loaded
    Sleep    2s
    Check Checkbox    //*[contains(@class,"pat-structure")]//input[contains(@class,"select-all")]
    Click    //a[@id="btn-selected-items"]
    Click    //a[contains(@class,"remove-all")]


no elements should be selected
    Get Checkbox State      //tr[@data-id="doc1"]//input    ==    unchecked
    Get Checkbox State      //tr[@data-id="doc2"]//input    ==    unchecked
    Get Checkbox State      //tr[@data-id="doc3"]//input    ==    unchecked
    Get Checkbox State      //tr[@data-id="doc4"]//input    ==    unchecked

I reorder the elements
    Click    //a[@id="btn-structure-rearrange"]
    Check Checkbox    //*[@id="popover-structure-rearrange"]//input[@name="reversed"]
    Click    //*[@id="popover-structure-rearrange"]//button[contains(text(),"Rearrange")]
    Wait For Condition    Text    //body    contains    Successfully rearranged folder

The Order Should Be
    [Arguments]    ${first}    ${second}    ${third}    ${fourth}
    Should be above    //tr[@data-id="doc${first}"]    //tr[@data-id="doc${second}"]
    Should be above    //tr[@data-id="doc${second}"]    //tr[@data-id="doc${third}"]
    Should be above    //tr[@data-id="doc${third}"]    //tr[@data-id="doc${fourth}"]

Should be above
    [Arguments]    ${locator1}    ${locator2}

    ${locator1-position}=    Get BoundingBox    ${locator1}    y
    ${locator2-position}=    Get BoundingBox    ${locator2}    y

    Should be true    ${locator1-position} < ${locator2-position}
