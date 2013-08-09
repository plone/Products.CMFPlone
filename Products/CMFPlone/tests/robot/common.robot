*** Settings ***

Resource  plone/app/robotframework/variables.robot

Library  Remote  ${PLONE_URL}/RobotRemote

*** Variables ***

${TEST_FOLDER}  test-folder

*** Keywords ***

a document
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/${TEST_FOLDER}/createObject?type_name=Document
    Wait until keyword succeeds  5s  1s  Element Should Be Visible  css=input#title
    Input text  name=title  ${title}
    Click Button  Save

a folder
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/${TEST_FOLDER}/createObject?type_name=Folder
    Wait until keyword succeeds  5s  1s  Element Should Be Visible  css=input#title
    Input text  name=title  ${title}
    Click Button  Save

a folder '${foldername}' with a document '${documentname}'
    Go to  ${PLONE_URL}/${TEST_FOLDER}/createObject?type_name=Folder
    Input text  name=title  ${foldername}
    Click Button  Save
    Go to  ${PLONE_URL}/${TEST_FOLDER}/folder/edit
    Input text  name=title  ${documentname}
    Click Button  Save

a collection
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/${TEST_FOLDER}/createObject?type_name=Collection
    Wait until keyword succeeds  5s  1s  Element Should Be Visible  css=input#title
    Input text  name=title  ${title}
    Click Button  Save

a site owner
    Enable autologin as  Site Administrator

the site root
    Go to  ${PLONE_URL}

a test folder
    Go to homepage
    Add folder  ${TEST_FOLDER}

the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}

there should be '${count}' livesearch results
    Wait until keyword succeeds  5s  1s  Element Should Be Visible  css=div#LSResult
    Wait until keyword succeeds  5s  1s  Xpath Should Match X Times  //div[@id = 'LSResult']/descendant::li  ${count}
