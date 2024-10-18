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


Fill text to tinymce editor
    [Arguments]    ${attr_name}    ${input}

    Wait For Condition    Attribute    //body    class    contains    patterns-loaded

    Sleep    1

    Evaluate JavaScript    //textarea[@name="${attr_name}"]
    ...    (elem, text) => {
    ...        elem["pattern-tinymce"].instance.tiny.setContent('${input}');
    ...    }
    ...    all_elements=False

    Sleep    2s

    ${check}=    Evaluate JavaScript    //textarea[@name="${attr_name}"]
    ...    (elem) => {
    ...        return elem["pattern-tinymce"].instance.tiny.getContent();
    ...    }
    ...    all_elements=False

    Should not be empty    ${check}


Pause
   Import library    Dialogs
   Pause execution
