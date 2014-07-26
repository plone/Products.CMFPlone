#[Documentation]
# bin/robot-server Products.CMFPlone.testing.PRODUCTS_CMFPLONE_ROBOT_TESTING
# bin/robot test_controlpanel_site.robot

*** Settings ***

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  common.robot

Test Setup  Open SauceLabs test browser
Test Teardown  Run keywords  Report test status  Close all browsers


*** Test Cases ***************************************************************

Scenario: Set Site Title in the Site Control Panel
  Given a logged-in site administrator
    and the site control panel
   When I set the site title to 'My Site'
   Then the site title should be set to 'My Site'

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


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

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

I enable dublin core metadata
  Select Checkbox  form.widgets.exposeDCMetaTags:list
  Click Button  Save
  Wait until page contains  Changes saved


# --- THEN -------------------------------------------------------------------

the site title should be set to '${expected_site_title}'
  Go To  ${PLONE_URL}
  ${actual_site_title}=  Get title
  Should be equal  ${actual_site_title}  ${expected_site_title}

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

