*** Settings ***

Variables  plone/app/testing/interfaces.py
Variables  variables.py

Library  Selenium2Library  timeout=${SELENIUM_TIMEOUT}  implicit_wait=${SELENIUM_IMPLICIT_WAIT}

Resource  keywords.txt

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
    Wait until page contains  ${portletname}
    Element should contain  portal-column-one  ${portletname}

I should see a '${portletname}' portlet in the right column
    Wait until page contains  ${portletname}
    Element should contain  portal-column-two  ${portletname}

I should not see '${text}' in the left column
    Flex Element should not exist  xpath=//div[@id="portal-column-one" and contains(.,"${text}")]

I should not see '${text}' in the right column
    Flex Element should not exist  xpath=//div[@id="portal-column-two" and contains(.,"${text}")]


