*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown

Variables    variables.py

*** Test Cases ***

Scenario: Set Site Title in the Site Control Panel
    Given a logged-in site administrator
      and the site control panel
     When I set the site title to 'My Site'
     Then the site title should be set to 'My Site'

Scenario: Set Site Logo in the Site Control Panel
    Given a logged-in site administrator
      and the site control panel
     When I set a custom logo
     Then the site logo should be set to the custom logo

Scenario: Enable Dublin Core Metadata in the Site Control Panel
    Given a logged-in site administrator
      and the site control panel
     When I enable dublin core metadata
     Then the dublin core metadata shows up on the site

Scenario: Enable Sitemap in the Site Control Panel
    Given a logged-in site administrator
      and the site control panel
     When I enable the sitemap
     Then then I can see a sitemap

Scenario: Add Webstats Javascript in the Site Control Panel
    Given a logged-in site administrator
      and the site control panel
     When I add a Javascript snippet to the webstats javascript
     Then the Javascript snippet shows up on the site


*** Keywords ***

# GIVEN

the site control panel
    Go to    ${PLONE_URL}/@@site-controlpanel
    Get Text    //body    contains    Site Settings


# WHEN

I enable the sitemap
    Check Checkbox    //input[@name="form.widgets.enable_sitemap:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I set the site title to '${site_title}'
    Type Text    //input[@name="form.widgets.site_title"]    ${site_title}
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I set a custom logo
    Upload File By Selector    //input[@name="form.widgets.site_logo"]    ${PATH_TO_TEST_FILES}/pixel.png
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I enable dublin core metadata
    Check Checkbox    //input[@name="form.widgets.exposeDCMetaTags:list"]
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved

I add a Javascript snippet to the webstats javascript
    Type Text    //textarea[@name="form.widgets.webstats_js"]    <script id="webstats_snippet"></script>
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


# THEN

the site title should be set to '${expected_site_title}'
    Go To    ${PLONE_URL}
    Get Text    //head/title    should be    ${expected_site_title}

the site logo should be set to the custom logo
    Go To    ${PLONE_URL}
    Get Element Count    //*[@id="portal-logo"]/img[contains(@src,'@@site-logo/pixel.png')]    should be    1

then I can see a sitemap

    Import library    OperatingSystem

    # this is for robotframework browser > 17
    Download    ${PLONE_URL}/sitemap.xml.gz    saveAs=/tmp/sitemap.xml.gz
    File Should Exist    /tmp/sitemap.xml.gz

    # this is for robotframework browser < 18.0
    # ${file_object}=    Download    ${PLONE_URL}/sitemap.xml.gz
    # File Should Exist    ${file_object.saveAs}

the dublin core metadata shows up on the site
    Go to    ${PLONE_URL}
    Get Element Count    //html/head/meta[@name="DC.date.modified"]    should be    1
    Get Element Count    //html/head/meta[@name="DC.format"]    should be    1
    Get Element Count    //html/head/meta[@name="DC.type"]    should be    1
    Get Element Count    //html/head/meta[@name="DC.date.created"]    should be    1
    Get Element Count    //html/head/meta[@name="DC.language"]    should be    1

the Javascript snippet shows up on the site
    Go to  ${PLONE_URL}
    Get Element Count    //*[@id="webstats_snippet"]    should be    1
