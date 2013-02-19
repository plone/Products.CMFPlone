*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5

Resource  Products/CMFPlone/tests/robot/keywords.txt

Variables  plone/app/testing/interfaces.py
Variables  Products/CMFPlone/tests/robot/variables.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Test cases ***

Scenario: Add Login Portlet
    Given a manage portlets view
     When I add a 'Login' portlet to the left column
     Then I should see a 'Login' portlet in the left column

Scenario: Add Calendar Portlet
    Given a manage portlets view
     When I add a 'Calendar' portlet to the left column
     Then I should see a 'Calendar' portlet in the left column



*** Keywords ***

Suite Setup
    Open browser  ${PLONE_URL}  browser=${BROWSER}  remote_url=${REMOTE_URL}  desired_capabilities=${DESIRED_CAPABILITIES}
    Given a site owner

Suite Teardown
    Close All Browsers

a manage portlets view
    Go to   ${PLONE_URL}/@@manage-portlets

I add a '${portletname}' portlet to the left column
    Select from list  xpath=//div[@id="portletmanager-plone-leftcolumn"]//select  ${portletname}

I add a '${portletname}' portlet to the right column
    Select from list  xpath=//div[@id="portletmanager-plone-rightcolumn"]//select  ${portletname}

I delete a '${portlet}'' portlet from the left column
    Click Link  xpath=//div[@id="portal-column-one"]//div[@class="portletHeader" and contains(.,"${portlet}")]//a[@class="delete"]  don't wait
    Wait until keyword succeeds  1s  10s  Flex Element Should not exist  xpath=//div[@id="portal-column-one"]//div[@class="portletHeader" and contains(.,"${portlet}")]

when I delete the '${portlet}' portlet from the right column
    Click Link  xpath=//div[@id="portal-column-two"]//div[@class="portletHeader" and contains(.,"${portlet}")]//a[@class="delete"]  don't wait
    Wait until keyword succeeds  1s  10s  Flex Element Should not exist  xpath=//div[@id="portal-column-two"]//div[@class="portletHeader" and contains(.,"${portlet}")]

I should see a '${portletname}' portlet in the left column
    Element should contain  portal-column-one  ${portletname}

I should see a '${portletname}' portlet in the right column
    Element should contain  portal-column-two  ${portletname}

I should not see '${text}' in the left column
    Flex Element should not exist  xpath=//div[@id="portal-column-one" and contains(.,"${text}")]

I should not see '${text}' in the right column
    Flex Element should not exist  xpath=//div[@id="portal-column-two" and contains(.,"${text}")]


