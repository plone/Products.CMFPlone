*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5

Resource  Products/CMFPlone/tests/robot/keywords.txt
Variables  plone/app/testing/interfaces.py
Variables  Products/CMFPlone/tests/robot/variables.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


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

Suite Setup
    Open browser  ${TEST_FOLDER}  browser=${BROWSER}  remote_url=${REMOTE_URL}  desired_capabilities=${DESIRED_CAPABILITIES}
    Given a site owner

Suite Teardown
    Close All Browsers

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
