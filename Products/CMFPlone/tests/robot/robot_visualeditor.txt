*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5

Resource  Products/CMFPlone/tests/robot/keywords.txt

Variables  plone/app/testing/interfaces.py
Variables  Products/CMFPlone/tests/robot/variables.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Variables ***

${TITLE} =  An edited page
${PAGE_ID} =  an-edited-page
${TEXT} =  Lorem ipsum. Lorizzle, my nizzle.


*** Test cases ***

Scenario: visual editor
  Given an edited page
   When i add text to the visual editor field
    and i click Save
   Then the text is in the page


*** Keywords ***

Suite Setup
    Open browser  ${PLONE_URL}  browser=${BROWSER}
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}
    Go to  ${PLONE_URL}/createObject?type_name=Document
    Input text  name=title  ${TITLE}
    Click Button  Save

Suite Teardown
    Close All Browsers

an edited page
    Go to  ${PLONE_URL}/${PAGE_ID}/edit

i add text to the visual editor field
    Select frame  text_ifr
    Input text  content  ${TEXT}
    Unselect Frame
    # Input text  xpath=//textarea[@id="text"]  ${TEXT}

i click Save
    Click Button  form.button.save

the text is in the page
    Element should contain  xpath=//div[@id="content-core"]  ${TEXT}