*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Test cases ***************************************************************

Scenario: Add Login Portlet
    Given a logged-in site administrator
      and a manage portlets view
     When I add a 'Login' portlet to the left column
     Then I should see a 'Login' portlet in the left column


*** Keywords *****************************************************************

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
