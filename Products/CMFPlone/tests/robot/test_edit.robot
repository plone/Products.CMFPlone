*** Settings *****************************************************************

Resource  plone/app/robotframework/keywords.robot
Resource  plone/app/robotframework/saucelabs.robot
Resource  plone/app/robotframework/selenium.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Variables ****************************************************************

${TITLE}  An edited page
${PAGE_ID}  an-edited-page


*** Test cases ***************************************************************

Scenario: A page is opened to edit
    Given a logged-in site administrator
      and an edited page
     Then i have the title input field
      and i can only see the default tab

Scenario: Switch tabs
    Given a logged-in site administrator
      and an edited page
     When i click the Categorization tab
     Then the Categorization tab is shown
      and no other tab is shown

Scenario: Adding a related item
    Pass Execution  Disabled until plone.app.widgets is merged
    # Order of the next two lines is important
    # First we're creating a new item and then editing the original page
    Given a logged-in site administrator
      and at least one other item
      and an edited page
     When i click the Categorization tab
      and i click the add related item button
      and an overlay pops up
      and i select a related item
      and i close the overlay
      and i save the page
     Then the related item is shown in the page

Scenario: DateTime widget follows form dropdowns values
    Pass Execution  Disabled until plone.app.widgets is merged
    Given a logged-in site administrator
      and an edited page
     When i click the Dates tab
      and i select a date using the dropdowns
      and i click the calendar icon
     Then popup calendar should have the same date

Scenario: Form dropdowns follows DateTime widget values
    Pass Execution  Disabled until plone.app.widgets is merged
    Given a logged-in site administrator
      and an edited page
     When i click the Dates tab
      and i click the calendar icon
      and i select a date using the widget
     Then form dropdowns should not have the default values anymore


*** Keywords *****************************************************************

# --- GIVEN ------------------------------------------------------------------

an edited page
    Create content  type=Document  title=${TITLE}
    Go to  ${PLONE_URL}/${PAGE_ID}/edit
    Wait until page contains  Edit Page


# --- WHEN -------------------------------------------------------------------

I have the title input field
    Element Should Be Visible  xpath=//fieldset[@id='fieldset-default']

I can only see the default tab
    Wait For Condition  return window.jQuery('.autotoc-nav .active:visible').length > 0
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-settings']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-dates']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-categorization']

I click the ${tab} tab
    Given patterns are loaded
    Click link  ${tab}

I click the add related item button
    Click Button  xpath=//input[contains(@class, 'addreference')]

I select a related item
    Click Element  xpath=//div[contains(@class, 'overlay')]//input[@class='insertreference']
    Wait until keyword succeeds  10s  1s  Xpath Should Match X Times  //ul[@id = 'ref_browser_items_relatedItems']/descendant::input  1

I close the overlay
   Click Element  xpath=//div[contains(@class, 'overlay')]//div[@class='close']

I save the page
   Click Button  Save

I select a date using the dropdowns
    Select From List By Label  xpath=//select[@id='edit_form_effectiveDate_0_year']  2001
    Select From List By Label  xpath=//select[@id='edit_form_effectiveDate_0_month']  January
    Select From List By Label  xpath=//select[@id='edit_form_effectiveDate_0_day']  01
    Select From List By Label  xpath=//select[@id='edit_form_effectiveDate_0_hour']  01
    Select From List By Label  xpath=//select[@id='edit_form_effectiveDate_0_minute']  00
    Select From List By Label  xpath=//select[@id='edit_form_effectiveDate_0_ampm']  AM

I click the calendar icon

    Click Element  xpath=//span[@id='edit_form_effectiveDate_0_popup']
    Element Should Be Visible  xpath=//div[@class='calendar']

I select a date using the widget
    Click Element  xpath=//div[@class='calendar']/table/thead/tr[2]/td[4]/div


# --- THEN -------------------------------------------------------------------

popup calendar should have the same date
    Element Text Should Be  xpath=//div[@class='calendar']//thead//td[@class='title']  January, 2001

form dropdowns should not have the default values anymore
    ${yearLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_year']
    Should Not Be Equal  ${yearLabel}  --
    ${monthLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_month']
    Should Not Be Equal  ${monthLabel}  --
    ${dayLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_day']
    Should Not Be Equal  ${dayLabel}  --

the related item is shown in the page
   Xpath Should Match X Times  //dl[@id = 'relatedItemBox']/dd  1

an overlay pops up
    Wait Until Page Contains Element  xpath=//div[contains(@class, 'overlay')]//input[@class='insertreference']

the categorization tab is shown
    Element Should Be Visible  xpath=//fieldset[@id='fieldset-categorization']

no other tab is shown
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-dates']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-default']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-settings']

at least one other item
    Go to  ${PLONE_URL}/++add++Document
    Given patterns are loaded
    Execute Javascript  $('#form-widgets-IDublinCore-title').val('${TITLE}'); return 0;
    Click Button  Save
