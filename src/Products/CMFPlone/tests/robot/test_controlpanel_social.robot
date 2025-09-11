*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: Social settings are provided
    Given a logged-in site administrator
      and the social control panel
     When I provide social settings
     Then social tags should exist for anonymous

Scenario: Social tags are disabled
    Given a logged-in site administrator
      and the social control panel
     When I provide social settings
     When I disable social
     Then social tags should not exist


*** Keywords ***

# GIVEN

the social control panel
    Go to  ${PLONE_URL}/@@social-controlpanel
    Get Text    //body    contains    Social Media Settings


# WHEN

I disable social
    Uncheck Checkbox    //input[@name="form.widgets.share_social_data:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I provide social settings
    Type Text    //input[@name="form.widgets.twitter_username"]    plonecms
    Type Text    //input[@name="form.widgets.facebook_app_id"]    123456
    Type Text    //input[@name="form.widgets.facebook_username"]    plonecms
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


# THEN

social tags should exist for anonymous
    Go to    ${PLONE_URL}
    Get Element Count    //meta[@name="twitter:site"]    should be    0
    Get Element Count    //meta[@property="og:article:publisher"]    should be    0
    Get Element Count    //meta[@property="fb:app_id"]    should be    0
    Disable autologin
    Go to     ${PLONE_URL}
    Get Element Count    //meta[@name="twitter:site"]    should be    1
    Get Element Count    //meta[@property="og:article:publisher"]    should be    1
    Get Element Count    //meta[@property="fb:app_id"]    should be    1

social tags should not exist
    Go to    ${PLONE_URL}
    Get Element Count    //meta[@name="twitter:site"]    should be    0
    Get Element Count    //meta[@property="og:article:publisher"]    should be    0
    Get Element Count    //meta[@property="fb:app_id"]    should be    0
