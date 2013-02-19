*** Settings ***

Library  Selenium2Library  timeout=10  implicit_wait=0.5

Variables  plone/app/testing/interfaces.py
Variables  Products/CMFPlone/tests/robot/variables.py

Suite Setup  Suite Setup
Suite Teardown  Suite Teardown


*** Variables ***

${TITLE} =  An edited page
${PAGE_ID} =  an-edited-page


*** Test cases ***

Scenario: A page is opened to edit
    Given an edited page
     Then i have the title input field
      and i can only see the default tab

Scenario: Switch tabs
    Given an edited page
     When i click the categorization tab
     Then the categorization tab is shown
      and no other tab is shown

Scenario: Adding a related item
    # Order of the next two lines is important
    # First we're creating a new item and then editing the original page
    Given at least one other item
      and an edited page
     When i click the categorization tab
      and i click the add related item button
      and an overlay pops up
      and i select a related item
      and i close the overlay
      and i save the page
     Then the related item is shown in the page

Scenario: DateTime widget follows form dropdowns values
    Given an edited page
     When i click the dates tab
      and i select a date using the dropdowns
      and i click the calendar icon
     Then popup calendar should have the same date

Scenario: Form dropdowns follows DateTime widget values
    Given an edited page
     When i click the dates tab
     and i click the calendar icon
     and i select a date using the widget
    Then form dropdowns should not have the default values anymore



*** Keywords ***

Suite Setup
    Open browser  ${PLONE_URL}  browser=${BROWSER}
    Log in  ${SITE_OWNER_NAME}  ${SITE_OWNER_PASSWORD}
    Go to  ${PLONE_URL}/createObject?type_name=Document
    Input text  name=title  ${TITLE}
    Click Button  Save

Suite Teardown
    Close All Browsers

Log in
    [Arguments]  ${userid}  ${password}
    Go to  ${PLONE_URL}/login_form
    Page should contain element  __ac_name
    Page should contain element  __ac_password
    Page should contain button  Log in
    Input text  __ac_name  ${userid}
    Input text  __ac_password  ${password}
    Click Button  Log in

an edited page
    Go to  ${PLONE_URL}/${PAGE_ID}/edit

i have the title input field
    Element Should Be Visible  xpath=//fieldset[@id='fieldset-default']

i can only see the default tab
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-settings']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-dates']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-categorization']

i click the ${tabid} tab
    Click link  xpath=//a[@id='fieldsetlegend-${tabid}']

the categorization tab is shown
    Element Should Be Visible  xpath=//fieldset[@id='fieldset-categorization']

no other tab is shown
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-dates']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-default']
    Element Should Not Be Visible  xpath=//fieldset[@id='fieldset-settings']

at least one other item
    Go to  ${PLONE_URL}/createObject?type_name=Document
    Input text  name=title  ${TITLE}
    Click Button  Save

i click the add related item button
    Click Button  xpath=//input[contains(@class, 'addreference')]

an overlay pops up
    Wait Until Page Contains Element  xpath=//div[contains(@class, 'overlay')]//input[@class='insertreference']

i select a related item
    Click Element  xpath=//div[contains(@class, 'overlay')]//input[@class='insertreference']
    Wait until keyword succeeds  10s  1s  Xpath Should Match X Times  //ul[@id = 'ref_browser_items_relatedItems']/descendant::input  1

i close the overlay
   Click Element  xpath=//div[contains(@class, 'overlay')]//div[@class='close']

i save the page
   Click Button  Save

the related item is shown in the page
   Xpath Should Match X Times  //dl[@id = 'relatedItemBox']/dd  1

i select a date using the dropdowns
    Select From List  xpath=//select[@id='edit_form_effectiveDate_0_year']  2001
    Select From List  xpath=//select[@id='edit_form_effectiveDate_0_month']  January
    Select From List  xpath=//select[@id='edit_form_effectiveDate_0_day']  01
    Select From List  xpath=//select[@id='edit_form_effectiveDate_0_hour']  01
    Select From List  xpath=//select[@id='edit_form_effectiveDate_0_minute']  00
    Select From List  xpath=//select[@id='edit_form_effectiveDate_0_ampm']  AM

i click the calendar icon

    Click Element  xpath=//span[@id='edit_form_effectiveDate_0_popup']
    Element Should Be Visible  xpath=//div[@class='calendar']

popup calendar should have the same date
    Element Text Should Be  xpath=//div[@class='calendar']//thead//td[@class='title']  January, 2001

i select a date using the widget
    Mouse Down  xpath=//div[@class='calendar']/table/thead/tr[2]/td[4]/div
    Mouse Up  xpath=//div[@class='calendar']/table/thead/tr[2]/td[4]/div

form dropdowns should not have the default values anymore
    ${yearLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_year']
    Should Not Be Equal  ${yearLabel}  --
    ${monthLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_month']
    Should Not Be Equal  ${monthLabel}  --
    ${dayLabel} =  Get Selected List Label  xpath=//select[@id='edit_form_effectiveDate_0_day']
    Should Not Be Equal  ${dayLabel}  --


