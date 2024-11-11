*** Keywords ***

# SETUP

Refresh JS/CSS resources
  # Not needed anymore, and it is breaking the Plone Zope 4 tests.
  # Keep the keyword for backwards compatibility purposes.
  Sleep  0.0000001

# GIVEN

a logged-in manager
    Enable autologin as
    ...    Manager

a logged-in member
    Enable autologin as
    ...    Member

a logged-in site administrator
    Enable autologin as
    ...    Site Administrator
    ...    Contributor
    ...    Reviewer


a document '${title}'
    Create content
    ...    type=Document
    ...    id=doc
    ...    title=${title}

a file '${title}'
    Create content
    ...    type=File
    ...    id=file
    ...    title=${title}

a news item '${title}'
    Create content
    ...    type=News Item
    ...    id=doc
    ...    title=${title}

an image '${title}'
    Create content
    ...    type=Image
    ...    id=doc
    ...    title=${title}

a folder '${title}'
    Create content
    ...    type=Folder
    ...    title=${title}

a folder with a document '${title}'
    ${folder_uid}=    Create content    type=Folder    title=folder
    Create content
    ...    type=Document
    ...    container=${folder_uid}
    ...    title=${title}

Remove line from textarea
    [Arguments]    ${fieldName}    ${value}

    Import library    String
    ${lines}=  Get Text    //textarea[@name="${fieldName}"]
    ${lines}=  Remove String    ${lines}    ${value}\n
    Type Text    //textarea[@name="${fieldName}"]    ${lines}


Click item in contenbrowser column
    [arguments]  ${colnumber}    ${itemposition}
    Wait For Condition    Element States    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[${colnumber}]/div[contains(@class, "levelItems")]/div[${itemposition}]    contains    visible
    Click    //div[contains(@class, "content-browser-wrapper")]//div[contains(@class, "levelColumns")]/div[${colnumber}]/div[contains(@class, "levelItems")]/div[${itemposition}]


Fill text to tinymce editor
    [Arguments]    ${text}

    Wait For Condition    Classes    //body    contains    patterns-loaded

    ${old} =    Set Selector Prefix    //div[contains(@class, "tox-edit-area")]//iframe >>>
    Wait for Condition    Element States    //body    contains    visible
    Type Text    //body    ${text}
    Wait for Condition    Text    //body   !=    ""
    Set Selector Prefix    ${old}

Fill source code to tinymce editor
    [Arguments]    ${source_code}

    Wait For Condition    Classes    //body    contains    patterns-loaded
    Wait For Condition    Element States    //div[contains(@class,"tox-tinymce") and @role="application"]    contains    visible
    Wait for Condition    Element States    //div[contains(@class, "tox-edit-area")]//iframe >>> body    contains    visible

    # Click the View menu button
    Click    //span[contains(@class,"tox-mbtn__select-label") and contains(text(),"View")]/parent::button
    Wait for Condition    Element States    //div[@class="tox-collection__group"]    contains    visible

    # Click the Source code menu button
    Click    //div[@class="tox-collection__item-label" and contains(text(),"Source code")]/parent::div

    # Open dialog for source code insert
    ${textarea}=    Get Element    //textarea[@class="tox-textarea"]
    Wait for Condition    Element States    ${textarea}    contains    visible
    Type Text    ${textarea}    ${source_code}
    # Save
    Click    //button[@class="tox-button" and contains(text(),"Save")]

    Wait for Condition    Text    //div[contains(@class, "tox-edit-area")]//iframe >>> body   !=    ""


Pause
   Import library    Dialogs
   Pause execution
