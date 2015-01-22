Documentation
...            $ bin/robot-server Products.CMFPlone.testing.PRODUCTS_CMFPLONE_ROBOT_TESTING
...            $ bin/robot test_controlpanel_site.robot

*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Variables  Products/CMFPlone/tests/robot/variables.py

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

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


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

the site control panel
  Go to  ${PLONE_URL}/@@site-controlpanel
  Wait until page contains  Site settings


# --- WHEN -------------------------------------------------------------------

I enable the sitemap
  Select Checkbox  form.widgets.enable_sitemap:list
  Click Button  Save
  Wait until page contains  Changes saved

I set the site title to '${site_title}'
  Input Text  name=form.widgets.site_title  ${site_title}
  Click Button  Save
  Wait until page contains  Changes saved

I set a custom logo
  Choose File  name=form.widgets.site_logo  ${PATH_TO_TEST_FILES}/pixel.png
  Click Button  Save
  Wait until page contains  Changes saved

I enable dublin core metadata
  Select Checkbox  form.widgets.exposeDCMetaTags:list
  Click Button  Save
  Wait until page contains  Changes saved

I add a Javascript snippet to the webstats javascript
  Input Text  name=form.widgets.webstats_js  <script id="webstats_snippet"></script>
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

the site title should be set to '${expected_site_title}'
  Go To  ${PLONE_URL}
  ${actual_site_title}=  Get title
  Should be equal  ${actual_site_title}  ${expected_site_title}

the site logo should be set to the custom logo
  Go To  ${PLONE_URL}
  Page should contain element  //*[@id="portal-logo"]/img[contains(@src,'@@site-logo/pixel.png')]
  
then I can see a sitemap
  Go to  ${PLONE_URL}/sitemap.xml.gz
  # We need a 'Download file' selenium2library keyword to test this:
  # https://github.com/rtomac/robotframework-selenium2library/issues/24

the dublin core metadata shows up on the site
  Go to  ${PLONE_URL}
  Wait until page contains  Powered by Plone
  Page should contain element  xpath=//html/head/meta[@name='DC.date.modified']
  Page should contain element  xpath=//html/head/meta[@name='DC.format']
  Page should contain element  xpath=//html/head/meta[@name='DC.type']
  Page should contain element  xpath=//html/head/meta[@name='DC.date.created']
  Page should contain element  xpath=//html/head/meta[@name='DC.language']

the Javascript snippet shows up on the site
  Go to  ${PLONE_URL}
  Wait until page contains  Powered by Plone
  Page should contain element  id=webstats_snippet
