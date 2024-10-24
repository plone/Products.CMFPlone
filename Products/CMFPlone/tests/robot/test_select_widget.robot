*** Settings ***

Resource  plone/app/robotframework/browser.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Resource  keywords.robot

Test Setup  Run keywords  Plone Test Setup
Test Teardown  Run keywords  Plone Test Teardown


*** Variables ***

${mockup_bootstrap_class}    pat-select2

${select_field_name}    form.widgets.select_field
${list_field_name}    form.widgets.list_field

${input_search}    //div[@id="select2-drop"]//div[contains(@class,"select2-search")]//input
${dropdown_multiple}    css=.select2-choices
${dropdown_select}    //a[@class="select2-choice"]
${results_label}    css=.select2-result-label


*** Test Cases ***

Scenario: The Select Widget has the class that bootstraps mockup JS
    Given a form
     Then the input fields have the mockup class

Scenario: The Select Widget allows to select a single value
    Given a logged-in member
      and a form
     When I select the option  3
     Then the widget shows the element  three

Scenario: The Select Widget autocomplete function works
    Given a logged-in member
      and a form
     When I type on the autocomplete field  wo
     Then the widget shows the element  two

The Select Multiple Widget allows to select multiple values
    Given a logged-in member
      and a form
     When I click on the element  2
      And I click on the element  1
     Then the widget shows two elements    five    four

Scenario: The Select Multiple Widget autocomplete function works
    Given a logged-in member
      and a form
     When I type on the multiple autocomplete field    s
     Then the widget shows one element    six


*** Keywords ***

# Given

a form
  Go to    ${PLONE_URL}/@@select-widget-view

# When


I select the option
    [Arguments]  ${index}
    Wait For Elements State    ${dropdown_select}    visible    timeout=2 s
    Open Dropdown    ${dropdown_select}    ${input_search}
    Click    css=li.select2-results-dept-0:nth-child(${index})

I type on the autocomplete field
    [Arguments]    ${text}
    Wait For Elements State    ${dropdown_select}    visible    timeout=2 s
    Open Dropdown    ${dropdown_select}    ${input_search}
    Type Text    ${input_search}    ${text}
    Click    ${results_label}

I click on the element
    [Arguments]  ${index}
    Wait For Elements State    ${dropdown_multiple}    visible    timeout=2 s
    Open Dropdown    ${dropdown_multiple}    ${dropdown_multiple}
    Focus    css=li.select2-results-dept-0:nth-child(${index})
    Click    css=li.select2-results-dept-0:nth-child(${index})

I type on the multiple autocomplete field
    [Arguments]    ${text}
    Wait For Elements State    ${dropdown_multiple}    visible    timeout=2 s
    Click    //ul[@class="select2-choices"]
    Type Text  css=.select2-input.select2-focused  ${text}
    Keyboard Key    press    Enter

# Then

the input fields have the mockup class
    Get Classes    //select[@name="${select_field_name}"]    contains    ${mockup_bootstrap_class}
    Get Classes    //select[@name="${list_field_name}"]    contains    ${mockup_bootstrap_class}

the widget shows the element
    [Arguments]    ${text}
    Get Text    css=.select2-chosen    should be    ${text}    messsage=${text} seems to not be selected


the widget shows two elements
    [Arguments]  ${first_string}  ${second_string}
    Get Text    li.select2-search-choice:nth-child(1) > div:nth-child(1)    contains    ${first_string}
    Get Text    li.select2-search-choice:nth-child(2) > div:nth-child(1)    contains    ${second_string}

the widget shows one element
    [Arguments]    ${string}
    Get Text    li.select2-search-choice:nth-child(1) > div:nth-child(1)    contains    ${string}

# dry

Open Dropdown
    [Arguments]    ${locator}    ${validaton}
    Click    ${locator}
    Wait For Elements State    ${validaton}    visible    timeout=2 s    message=The dropdown did not show up at location ${validaton}