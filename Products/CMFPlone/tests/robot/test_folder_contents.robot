*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test cases ***

Scenario: Select All items
    Given a site owner
      And a test folder
      And four dummy pages on test folder
      And the folder contents view
     When I select all the elements
     Then the informative string appears
      And the four elements got selected
      And the clear selection link appears

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

*** Keywords ***

the folder contents view
    Go to  ${PLONE_URL}/${TEST_FOLDER}/folder_contents

I click the '${link_name}' link
    Click Link  ${link_name}

four dummy pages on test folder
    a document 'doc1' in the test folder
    a document 'doc2' in the test folder
    a document 'doc3' in the test folder
    a document 'doc4' in the test folder

a document '${title}' in the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}/createObject?type_name=Document
    Input text  name=title  ${title}
    Click Button  Save

I select all the elements
    Click Element  id=foldercontents-selectall

the four elements got selected
    Checkbox Should Be Selected  id=cb_doc1
    Checkbox Should Be Selected  id=cb_doc2
    Checkbox Should Be Selected  id=cb_doc3
    Checkbox Should Be Selected  id=cb_doc4

the informative string appears
    # The response contained a newline and Selenium was unable to recognize the
    # full message correctly. So we are forced to check for it only partially.
    Wait until page contains  All 4 items in this folder
    Page Should Contain  All 4 items in this folder

the clear selection link appears
    Page Should Contain Element  id=foldercontents-clearselection

I clear the selection
    Click link  Clear selection

no elements should be selected
    Checkbox Should Not Be Selected  id=cb_doc1
    Checkbox Should Not Be Selected  id=cb_doc2
    Checkbox Should Not Be Selected  id=cb_doc3
    Checkbox Should Not Be Selected  id=cb_doc4

the order should be 1 > 2 > 3 > 4
    Should be above  css=tr#folder-contents-item-doc1  css=tr#folder-contents-item-doc2
    Should be above  css=tr#folder-contents-item-doc2  css=tr#folder-contents-item-doc3
    Should be above  css=tr#folder-contents-item-doc3  css=tr#folder-contents-item-doc4

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
