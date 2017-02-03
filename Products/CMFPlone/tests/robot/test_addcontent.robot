*** Settings *****************************************************************


Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot


Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test cases ***************************************************************

Scenario: Add a content called layout
    Given A Logged In Site Administrator
      and a folder 'my-folder' with a document 'layout'
     When I open folder contents
     Then it shows one element

Scenario: Edit a content called layout
    Given A Logged In Site Administrator
      and a folder 'my-folder' with a document 'layout'
     When I edit the folder
     Then The edit form is shown


*** Keywords *****************************************************************

I open folder contents
    Go to  ${PLONE_URL}/${TEST_FOLDER}/my-folder/folder_contents
    Page should contain element  css=.pat-structure
    Given patterns are loaded

it shows one element
    Go to  ${PLONE_URL}/${TEST_FOLDER}/my-folder/folder_contents
    Page should contain element  css=.pat-structure
    Given patterns are loaded
    Execute Javascript  $('.pat-structure table tbody tr').length == 1; return 0;

I edit the folder
   Go to  ${PLONE_URL}/${TEST_FOLDER}/my-folder/edit

The edit form is shown
   Element Should Be Visible  xpath=//fieldset[@id='fieldset-default']
