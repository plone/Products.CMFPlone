*** Settings ***

Resource  plone/app/robotframework/variables.robot

Library  Remote  ${PLONE_URL}/RobotRemote

*** Variables ***

${TEST_FOLDER}  test-folder

*** Keywords ***

a document
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/${TEST_FOLDER}/++add++Document
    Given patterns are loaded
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('${title}'); return 0;
    Click Button  Save

a folder
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/${TEST_FOLDER}/++add++Folder
    Given patterns are loaded
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('${title}'); return 0;
    Click Button  Save

a folder '${foldername}' with a document '${documentname}'
    Go to  ${PLONE_URL}/${TEST_FOLDER}/++add++Folder
    Given patterns are loaded
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('${foldername}'); return 0;
    Click Button  Save
    Go to  ${PLONE_URL}/${TEST_FOLDER}/folder/edit
    Given patterns are loaded
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('${documentname}'); return 0;
    Click Button  Save

a collection
    [Arguments]  ${title}
    Go to  ${PLONE_URL}/${TEST_FOLDER}/++add++Collection
    Given patterns are loaded
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('${title}'); return 0;
    Click Button  Save

a site owner
    Log in as site owner

the site root
    Go to  ${PLONE_URL}

a test folder
    Go to  ${PLONE_URL}/++add++Folder
    Given patterns are loaded
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('Test Folder'); return 0;
    Click Button  Save

the test folder
    Go to  ${PLONE_URL}/${TEST_FOLDER}

there should be '${count}' livesearch results
    Wait until keyword succeeds  5s  1s  Element Should Be Visible  css=div#LSResult
    Wait until keyword succeeds  5s  1s  Xpath Should Match X Times  //div[@id = 'LSResult']/descendant::li  ${count}

patterns are loaded
    Wait For Condition  return $('body.patterns-loaded').size() > 0
