*** Settings ***

Resource    plone/app/robotframework/browser.robot
Resource    keywords.robot

Library    Remote    ${PLONE_URL}/RobotRemote

Test Setup    Run Keywords    Plone test setup
Test Teardown    Run keywords     Plone test teardown


*** Test Cases ***

Scenario: Configure Filter Control Panel to filter out nasty tags
    Given a logged-in site administrator
      and the filter control panel
     When I add 'h1' to the nasty tags list and remove it from the valid tags list
     Then the 'h1' tag is filtered out when a document is saved

Scenario: Configure Filter Control Panel to strip out tags
    Given a logged-in site administrator
      and the filter control panel
     When I remove 'h1' from the valid tags list
     Then the 'h1' tag is stripped when a document is saved

Scenario: Configure Filter Control Panel to allow custom tags
    Given a logged-in site administrator
      and the filter control panel
     When I add 'foobar' to the valid tags list
     Then the 'foobar' tag is preserved when a document is saved

Scenario: Configure Filter Control Panel to allow custom attributes
    Given a logged-in site administrator
      and the filter control panel
     When I add 'foo-foo' to the custom attributes list
     Then the 'foo-foo' attribute is preserved when a document is saved

Scenario: Filter Control Panel displays information regarding caching when saved
    Given a logged-in site administrator
      and the filter control panel
     When I save the form
     Then success message should contain information regarding caching


*** Keywords ***

# GIVEN

the filter control panel
    Go to    ${PLONE_URL}/@@filter-controlpanel

# WHEN

I add '${tag}' to the nasty tags list and remove it from the valid tags list
    Type Text    //textarea[@name="form.widgets.nasty_tags"]    ${tag}
    Remove line from textarea    form.widgets.valid_tags    ${tag}
    I save the form


I save the form
    Click    //button[@name="form.buttons.save"]
    Get Text    //body    contains    Changes saved


I remove '${tag}' from the valid tags list
    Remove line from textarea    form.widgets.valid_tags    ${tag}
    I save the form


I add '${tag}' to the valid tags list
    Type Text    //textarea[@name="form.widgets.valid_tags"]    ${tag}
    I save the form
    Get Text    //textarea[@name="form.widgets.valid_tags"]    contains    ${tag}


I add '${tag}' to the custom attributes list
    Type Text    //textarea[@name="form.widgets.custom_attributes"]    ${tag}
    I save the form
    Get Text    //textarea[@name="form.widgets.custom_attributes"]    contains    ${tag}

# THEN

the 'h1' tag is filtered out when a document is saved

    ${doc1_uid}=    Create content
    ...    id=doc1
    ...    title=Document 1
    ...    type=Document
    Go To    ${PLONE_URL}/doc1/edit
    Fill text to tinymce editor    heading\nSpanish Inquisition
    Mark text heading as h1 in tinymce editor
    I save the form
    Get Text    //body    contains    Spanish Inquisition
    Get Text    //body    not contains    heading


the 'h1' tag is stripped when a document is saved

    ${doc1_uid}=    Create content
    ...    id=doc1
    ...    title=Document 1
    ...    type=Document
    Go To  ${PLONE_URL}/doc1/edit
    Fill text to tinymce editor    heading\nSpanish Inquisition
    Mark text heading as h1 in tinymce editor
    I save the form
    Get Text    //body    contains    Spanish Inquisition
    Get Text    //body    contains    heading
    Get Element Count    //div[@id='content-core']//h1    should be    0    message=h1 should have been stripped out


the '${tag}' tag is preserved when a document is saved

    ${doc1_uid}=    Create content
    ...    id=doc1
    ...    title=Document 1
    ...    type=Document
    Go To    ${PLONE_URL}/doc1/edit
    Fill source code to tinymce editor    <${tag}>lorem ipsum</${tag}><p>Spanish Inquisition</p>
    I save the form
    Get Text    //body    contains    Spanish Inquisition
    Get Element Count    //div[@id='content-core']//${tag}    should be    1    message=the ${tag} tag should have been preserved


the '${attribute}' attribute is preserved when a document is saved

    ${doc1_uid}=  Create content
    ...    id=doc1
    ...    title=Document 1
    ...    type=Document
    Go To    ${PLONE_URL}/doc1/edit
    Fill source code to tinymce editor    <span ${attribute}="foo">lorem ipsum</span><p>Spanish Inquisition</p>
    I save the form
    Get Text    //body    contains    Spanish Inquisition
    Get Element Count    //span[@${attribute}]    should be    1    message=the ${attribute} tag should have been preserved


success message should contain information regarding caching
    Get Text    //*[contains(@class,"alert-warning")]    contains    HTML generation is heavily cached across Plone. You may have to edit existing content or restart your server to see the changes.


# DRY

Mark text heading as h1 in tinymce editor

    # select the text `heading` via javascript
    Evaluate JavaScript    //div[contains(@class, 'tox-edit-area')]//iframe
    ...    (elem, args) => {
    ...        let iframe_document = elem.contentDocument;
    ...        let body = iframe_document.body;
    ...        let p = body.firstChild;
    ...        let range = new Range();
    ...        range.setStart(p.firstChild, 0);
    ...        range.setEnd(p.firstChild, 7);
    ...        iframe_document.getSelection().removeAllRanges();
    ...        iframe_document.getSelection().addRange(range);
    ...    }
    ...    all_elements=False
    # here we use the editor to format the text `heading` with h1
    Click    //button[@aria-label="Formats"]
    Hover    //div[@title="Headers"]
    Click    //h1[contains(text(), "Header 1")]
