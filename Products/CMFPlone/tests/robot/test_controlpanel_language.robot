*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown

*** Test Cases ***

Scenario: Set Site Language in the Language Control Panel
    Given a logged-in site administrator
      and the language control panel
     When I set the site language to German
     Then the Plone user interface is in German


*** Keywords ***

# GIVEN

the language control panel
    Go to  ${PLONE_URL}/@@language-controlpanel
    Get Text    //body    contains    Language Settings


# WHEN

I set the site language to German
    Select Options By    //select[@name="form.widgets.default_language:list"]    label    Deutsch
    Select Options By    //select[@name="form.widgets.available_languages.from"]    label    Deutsch
    Click    //button[@value="→"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved.


# THEN

the Plone user interface is in German
    Go to    ${PLONE_URL}
    Get Text    //body    contains    Lizensiert unter der
