*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Open SauceLabs test browser  Refresh JS/CSS resources
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test cases ***************************************************************

Scenario: Select All items
    Given a logged-in site administrator
      and a folder with four pages
      and the folder contents view
     When I select all the elements
     Then the selection count appears
      and the four elements got selected
      and the clear selection link appears

#Scenario: Clear selection
#    Given a site owner
#      And four dummy pages on test folder
#      And the folder contents view
#      And I select all the elements
#     When I clear the selection
#     Then no elements should be selected

# XXX: This scenario only works on Firefox. In Chrome fails to do the Mouse Up
# and Mouse Down correctly.
#Scenario: Reorder Folder Contents
#    Given a site owner
#      And four dummy pages on test folder
#     When the folder contents view
#     Then the order should be 1 > 2 > 3 > 4
#     When I reorder the elements
#     Then the new order should be 4 > 3 > 2 > 1

*** Keywords *****************************************************************

a folder with four pages
    ${folder_uid}=  Create content  type=Folder  title=My Folder
    Create content  type=Document  title=Doc1  container=${folder_uid}
    Create content  type=Document  title=Doc2  container=${folder_uid}
    Create content  type=Document  title=Doc3  container=${folder_uid}
    Create content  type=Document  title=Doc4  container=${folder_uid}

the folder contents view
    Go to  ${PLONE_URL}/my-folder/folder_contents
    Page should contain element  css=.pat-structure
    Given folder contents pattern loaded

I click the '${link_name}' link
    Click Link  ${link_name}

I select all the elements
    Element should be visible  css=.pat-structure .select-all
    Click Element  css=.pat-structure .select-all

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
    Click link  id=selected
    Click link  css=a.remove-all

no elements should be selected
    Checkbox Should Not Be Selected  css=tr[data-id="doc1"] input
    Checkbox Should Not Be Selected  css=tr[data-id="doc2"] input
    Checkbox Should Not Be Selected  css=tr[data-id="doc3"] input
    Checkbox Should Not Be Selected  css=tr[data-id="doc4"] input

the order should be 1 > 2 > 3 > 4
    Should be above  css=tr[data-id="doc1"]  css=tr[data-id="doc2"]
    Should be above  css=tr[data-id="doc2"]  css=tr[data-id="doc3"]
    Should be above  css=tr[data-id="doc3"]  css=tr[data-id="doc4"]

I reorder the elements
    # Moving items could fail on a fast computer
    Set Selenium Speed  0.1 seconds

    # Moves the doc2 page above the doc1 page
    Reorder Element  folder-contents-item-doc1  folder-contents-item-doc2

    # Moves the doc4 page above the doc2 page
    Reorder Element  folder-contents-item-doc4  folder-contents-item-doc3
    Reorder Element  folder-contents-item-doc4  folder-contents-item-doc1
    Reorder Element  folder-contents-item-doc4  folder-contents-item-doc2

    # Moves the doc3 page above the doc2 page
    Reorder Element  folder-contents-item-doc3  folder-contents-item-doc1
    Reorder Element  folder-contents-item-doc3  folder-contents-item-doc2

    # Go back to normal speed
    Set Selenium Speed  0 seconds

the new order should be 4 > 3 > 2 > 1
    Should be above  css=tr#folder-contents-item-doc4  css=tr#folder-contents-item-doc3
    Should be above  css=tr#folder-contents-item-doc3  css=tr#folder-contents-item-doc2
    Should be above  css=tr#folder-contents-item-doc2  css=tr#folder-contents-item-doc1

Reorder Element
    [arguments]  ${element}  ${destination}

    Mouse Down  xpath=//tr[@id='${element}']/td
    Mouse Up    xpath=//tr[@id='${destination}']/td
    Mouse Out   xpath=//tr[@id='${element}']/td

Should be above
    [Arguments]  ${locator1}  ${locator2}

    ${locator1-position} =  Get vertical position  ${locator1}
    ${locator2-position} =  Get vertical position  ${locator2}
    Should be true  ${locator1-position} < ${locator2-position}

folder contents pattern loaded
    Wait For Condition  return $('.pat-structure div.navbar').size() > 0
