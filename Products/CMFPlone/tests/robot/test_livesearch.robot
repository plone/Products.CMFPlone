*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Run keywords  Open SauceLabs test browser  Background
Test Teardown  Run keywords  Report test status  Close all browsers

*** Test cases ***

Scenario: Simple Livesearch
    Given a document  Welcome to Plone
     When I search for  Welcome
     Then the livesearch results should contain  Welcome to Plone
      and there should be '2' livesearch results

Scenario: Livesearch for documents
    Given a document  My document
     When I search for  My document
     Then the livesearch results should contain  My document
      and there should be '2' livesearch results

Scenario: Livesearch for folder
    Given a folder  My folder
     When I search for  My folder
     Then the livesearch results should contain  My folder
      and there should be '2' livesearch results

Scenario: Livesearch in current folder only
    Given a folder 'folder' with a document 'Inside Document'
      and a document  Outside Document
     When I search the currentfolder only for  Inside Document
     Then the livesearch results should contain  Inside Document
      and the livesearch results should not contain  Outside Document
      and there should be '2' livesearch results


*** Keywords ***

Background
    Given a site owner
      and a test folder

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
