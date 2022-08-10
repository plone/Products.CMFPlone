*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test cases ***************************************************************


Scenario: Select All items
    Given a logged-in site administrator
      and a folder with four pages
      and the folder contents view
     When I select all the elements
     Then the selection count appears
      and the four elements got selected
      and the clear selection link appears

Scenario: Clear selection
   Given a logged-in site administrator
     and a folder with four pages
     and the folder contents view
     And I select all the elements
    When I clear the selection
    Then no elements should be selected

Scenario: Reorder Folder Contents
   Given a logged-in site administrator
     and a folder with four pages
     and the folder contents view
    Then The Order Should Be  1   2   3   4
    When I reorder the elements
    Then The Order Should Be  4   3   2   1


*** Keywords *****************************************************************


a folder with four pages
    ${folder_uid}=  Create content  type=Folder  title=My Folder
    Create content  type=Document  title=Doc1  container=${folder_uid}
    Create content  type=Document  title=Doc2  container=${folder_uid}
    Create content  type=Document  title=Doc3  container=${folder_uid}
    Create content  type=Document  title=Doc4  container=${folder_uid}

the folder contents view
    Go to  ${PLONE_URL}/my-folder/folder_contents
    Given folder contents pattern loaded

I click the '${link_name}' link
    Click Link  ${link_name}

I select all the elements
    Wait until page contains element  css=.pat-structure .select-all
    Wait until page contains element  css=.itemRow
    ${select_all_selector}  Set Variable  .pat-structure .select-all
    Wait Until Element Is Visible  css=${select_all_selector}
    Click Element  css=${select_all_selector}

the four elements got selected
    Checkbox Should Be Selected  css=tr[data-id="doc1"] input
    Checkbox Should Be Selected  css=tr[data-id="doc2"] input
    Checkbox Should Be Selected  css=tr[data-id="doc3"] input
    Checkbox Should Be Selected  css=tr[data-id="doc4"] input

the selection count appears
    Wait until page contains element  css=#btn-selected-items .label-success
    Element Should Contain  css=#btn-selected-items .label-success  4

the clear selection link appears
    Page Should Contain Element  css=a.remove-all

I clear the selection
    Click link  id=btn-selected-items
    Click link  css=a.remove-all

no elements should be selected
    Checkbox Should Not Be Selected  css=tr[data-id="doc1"] input
    Checkbox Should Not Be Selected  css=tr[data-id="doc2"] input
    Checkbox Should Not Be Selected  css=tr[data-id="doc3"] input
    Checkbox Should Not Be Selected  css=tr[data-id="doc4"] input

I reorder the elements
    Click link  css=#btn-structure-rearrange
    Click element  name=reversed
    Click button  css=#popover-structure-rearrange .btn-primary
    Wait until page contains  Successfully rearranged folder

The Order Should Be
    [Arguments]  ${first}  ${second}  ${third}  ${fourth}
    Should be above  css=tr[data-id="doc${first}"]   css=tr[data-id="doc${second}"]
    Should be above  css=tr[data-id="doc${second}"]  css=tr[data-id="doc${third}"]
    Should be above  css=tr[data-id="doc${third}"]   css=tr[data-id="doc${fourth}"]

Should be above
    [Arguments]  ${locator1}  ${locator2}

    ${locator1-position} =  Get vertical position  ${locator1}
    ${locator2-position} =  Get vertical position  ${locator2}
    Should be true  ${locator1-position} < ${locator2-position}
