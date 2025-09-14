*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Variables    variables.py

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test cases ***

Scenario: Add Login Portlet to left column
    Given a logged-in site administrator
      and a manage portlets view
     When I add a 'Login' portlet to the left column
      and I go to portal root
     Then I should see a 'Login' portlet in the left column

Scenario: Add Login Portlet to right column
    Given a logged-in site administrator
      and a manage portlets view
     When I add a 'Login' portlet to the right column
      and I go to portal root
     Then I should see a 'Login' portlet in the right column

Scenario: Delete Login Portlet from left column
    Given a logged-in site administrator
      and a manage portlets view
     When I add a 'Login' portlet to the left column
      and I delete a 'Login' portlet from the left column
      and I go to portal root
     Then I should not see a 'Login' portlet in the left column

Scenario: Delete Login Portlet from right column
    Given a logged-in site administrator
      and a manage portlets view
     When I add a 'Login' portlet to the right column
      and I delete a 'Login' portlet from the right column
      and I go to portal root
     Then I should not see a 'Login' portlet in the right column

# TODO: Move Portlets Up and Down
*** Keywords ***

# Given

a manage portlets view
    Go to    ${PLONE_URL}/@@manage-portlets
    Get Text    //body    contains    Manage portlets

# When

I add a '${portletname}' portlet to the left column
    Select Options By    //div[@id="portletmanager-plone-leftcolumn"]//select[contains(@class,"add-portlet")]    label    ${portletname}
    Get Text    //body    contains    Portlet added

I add a '${portletname}' portlet to the right column
    Select Options By    //div[@id="portletmanager-plone-rightcolumn"]//select[contains(@class,"add-portlet")]    label    ${portletname}
    Get Text    //body    contains    Portlet added

I go to portal root
    Disable autologin
    Go to    ${PLONE_URL}

I delete a '${portlet}' portlet from the left column
    Click    //*[@id="portletmanager-plone-leftcolumn"]/div[2]/div[2]/div[2]/form[3]/button
    Get Element Count    //*[@id="portletmanager-plone-leftcolumn"]//div[@class="portletAssignment"]    <=    1

I delete a '${portlet}' portlet from the right column
    Click    //*[@id="portletmanager-plone-rightcolumn"]/div[2]/div[2]/div[2]/form[3]/button
    Get Element Count    //*[@id="portletmanager-plone-rightcolumn"]//div[@class="portletAssignment"]    <=    1


# Then
I should see a '${portletname}' portlet in the left column
    Get Element Count    //*[@id="portal-column-one"]//div[contains(@class,"portlet${portletname}")]    should be    1

I should see a '${portletname}' portlet in the right column
    Get Element Count    //*[@id="portal-column-two"]//div[contains(@class,"portlet${portletname}")]    should be    1

I should not see a '${text}' portlet in the left column
    Get Element Count    //*[@id="portal-column-one"]//div[contains(@class,"portlet${text}")]    should be    0

I should not see a '${text}' portlet in the right column
    Get Element Count    //*[@id="portal-column-two"]//div[contains(@class,"portlet${text}")]    should be    0
