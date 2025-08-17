*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Variables ***

${TITLE}  An edited page
${LINK_TITLE}  An edited link item
${PAGE_ID}  an-edited-page
${LINK_ID}  an-edited-link-item


*** Test cases ***

Scenario: A page is opened to edit
    Given a logged-in site administrator
      and an edited page
     Then i have the title input field
      and i can only see the default tab

Scenario: Switch tabs
    Given a logged-in site administrator
      and an edited page
     When i click the 'Categorization' tab
     Then the Categorization tab is shown
      and no other tab is shown

Scenario: Adding a related item
    # Order of the next two lines is important
    # First we're creating a new item and then editing the original page
    Given a logged-in site administrator
      and at least one other item
      and an edited page
     When i click the 'Categorization' tab
      and i select a related item
      and i save the page
     Then the related item is shown in the page

Scenario: DateTime widget follows form dropdowns values
    Pass Execution  Disabled because of browser native datepicker
    Given a logged-in site administrator
      and an edited page
     When i click the Dates tab
      and i select a date using the dropdowns
      and i click the calendar icon
     Then popup calendar should have the same date

Scenario: Form dropdowns follows DateTime widget values
    Pass Execution  Disabled because of browser native datepicker
    Given a logged-in site administrator
      and an edited page
     When i click the Dates tab
      and i click the calendar icon
      and i select a date using the widget
     Then form dropdowns should not have the default values anymore

Scenario: A link item is opened to edit
    Given a logged-in site administrator
      and an edited link item
     Then i have the title input field
      and i can only see the default tab

Scenario: Add an internal link to linked item
    Given a logged-in site administrator
      and at least one other item
      and an edited link item
      and i select a linked item
      and i save the page
     Then the linked item is shown in the page
      and Capture page screenshot and log source

*** Keywords ***

# GIVEN

an edited page
    Create content
    ...    type=Document
    ...    title=${TITLE}
    Go to    ${PLONE_URL}/${PAGE_ID}/edit
    Get Text    //body    contains    Edit Page

an edited link item
    Create content
    ...    type=Link
    ...    title=${LINK_TITLE}
    Go to    ${PLONE_URL}/${LINK_ID}/edit
    Get Text    //body    contains    Edit Link


# WHEN

I have the title input field
    Get Element States    //fieldset[@id='fieldset-default']    contains    visible

I can only see the default tab
    Get Element States    //fieldset[@id='fieldset-default']    contains    visible
    Get Element States    //fieldset[@id='fieldset-dates']    not contains    visible
    Get Element States    //fieldset[@id='fieldset-categorization']   not contains    visible

I click the ${tab} tab
    Click    //a[contains(text(),${tab})]

I select a related item
    # Click the select button
    Click    //div[@id="formfield-form-widgets-IRelatedItems-relatedItems"]//a[contains(@class, "btn-primary")]
    # Click first element in first column
    Click item in contenbrowser column    1    1
    # Click the select Button in the Toolbar of column 2
    Click    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[2]/div[contains(@class, "levelToolbar")]//button[contains(@class, "btn-outline-primary")]

I select a linked item
    # Click the select button
    Click  //div[@id="formfield-form-widgets-remoteUrl"]//a[contains(@class, "btn-primary")]
    # Click first element in first column
    Click item in contenbrowser column    1    1
    # Click the select Button in the Toolbar of column 2
    # This selects the "test-folder"
    Click    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[2]/div[contains(@class, "levelToolbar")]//button[contains(@class, "btn-outline-primary")]

I save the page
    Click    //button[@name="form.buttons.save"]

I click the calendar icon
    Click    //span[@id='edit_form_effectiveDate_0_popup']
    Get Element States    //div[@class='calendar']   contains    visible

I select a date using the widget
    Click    //div[@class='calendar']/table/thead/tr[2]/td[4]/div


# THEN

popup calendar should have the same date
    Get Text    //div[@class='calendar']//thead//td[@class='title']    should be    January, 2001

form dropdowns should not have the default values anymore
    ${yearLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_year']
    Should Not Be Equal  ${yearLabel}  --
    ${monthLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_month']
    Should Not Be Equal  ${monthLabel}  --
    ${dayLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_day']
    Should Not Be Equal  ${dayLabel}  --

the related item is shown in the page
    Get Element Count    //*[@id="section-related"]    should be    1

the linked item is shown in the page
    # check if the selected testfolder is linked
    Get Element Count    //a[@href='${PLONE_URL}/test-folder']    greater than    0


an overlay pops up
    Get Element Count    //div[contains(@class, 'overlay')]//input[@class='insertreference']    should be    1

the categorization tab is shown
    Get Element States    //fieldset[@id='fieldset-categorization']    contains    visible

no other tab is shown
    Get Element States    //fieldset[@id='fieldset-dates']    not contains    visible
    Get Element States    //fieldset[@id='fieldset-default']    not contains    visible
    Get Element States    //fieldset[@id='fieldset-settings']    not contains    visible

at least one other item
    Go to    ${PLONE_URL}/++add++Document
    Wait For Condition    Classes    //body    contains    patterns-loaded
    Type Text    //input[@id="form-widgets-IDublinCore-title"]    ${TITLE}
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Item created
