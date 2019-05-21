*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test cases ***************************************************************

Scenario: Simple Livesearch
    Pass Execution  Disabled until livesearch pattern is integrated
    Given a logged-in site administrator
      and a document  Welcome to Plone
     When I search for  Welcome
     Then the livesearch results should contain  Welcome to Plone
      and there should be '2' livesearch results

Scenario: Livesearch for documents
    Pass Execution  Disabled until livesearch pattern is integrated
    Given a logged-in site administrator
      and a document  My document
     When I search for  My document
     Then the livesearch results should contain  My document
      and there should be '2' livesearch results

Scenario: Livesearch for folder
    Pass Execution  Disabled until livesearch pattern is integrated
    Given a logged-in site administrator
      and a folder  My folder
     When I search for  My folder
     Then the livesearch results should contain  My folder
      and there should be '2' livesearch results

Scenario: Livesearch in current folder only
    Pass Execution  Disabled until livesearch pattern is integrated
    Given a logged-in site administrator
      and a folder with a document 'Inside Document'
      and a document  Outside Document
     When I search the currentfolder only for  Inside Document
     Then the livesearch results should contain  Inside Document
      and the livesearch results should not contain  Outside Document
      and there should be '2' livesearch results


*** Keywords *****************************************************************

I search for
    [Arguments]  ${searchtext}
    Input text  css=input#searchGadget  ${searchtext}
    Focus  css=input#searchGadget

I search the currentfolder only for
    [Arguments]  ${searchtext}
    Select checkbox  id=searchbox_currentfolder_only
    Input text  css=input#searchGadget  ${searchtext}
    Focus  css=input#searchGadget

the livesearch results should contain
    [Arguments]  ${text}
    Wait until keyword succeeds  5s  1s  Element should contain  css=#LSResult .LSRow a  ${text}

the livesearch results should not contain
    [Arguments]  ${text}
    Wait until keyword succeeds  5s  1s  Page should not contain  css=#LSResult .LSRow a  ${text}
