*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown



*** Test Cases ***

Show contentrules
    Go to  ${PLONE_URL}/@@rules-controlpanel

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/contentrules-start.png
            ...  css=#content
            ...  css=div.plone-toolbar-container

add rule
    Go to  ${PLONE_URL}/+rule/plone.ContentRule
    Wait until element is visible
    ...  css=#formfield-form-widgets-title
    Click element  css=#form-widgets-title
    Input text  css=#form-widgets-title  Send Email when any Page is Modified

    Click element  css=#form-widgets-description
    Input text  css=#form-widgets-description  this rule is meant for folders where new staff is having a go
    Click element  css=#formfield-form-widgets-event
    Select From List By Label  id=form-widgets-event  Object modified


    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/contentrules-add.png
            ...  css=#content
    Click button  css=#form-buttons-save
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/contentrules-conditions.png
            ...  css=#content
    Wait until element is visible
    ...  name=form.button.Save
    Click button  name=form.button.Save


assign rule
    Go to  ${PLONE_URL}/news
    Click link  css=#contentview-contentrules a
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/contentrules-assign.png
            ...  css=#content
            ...  css=div.plone-toolbar-container

Edit folder
    Go to  ${PLONE_URL}
    Click element  css=#contentview-folderContents a
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-cutpaste.png
    ...  css=#content

Deleting content
    Go to  ${PLONE_URL}
    Click element  css=#contentview-folderContents a
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-delete.png
    ...  css=#content

Edit Page
    Go to  ${PLONE_URL}
    Click element  css=#contentview-edit a
    Wait until element is visible
    ...  css=#mceu_16-body
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/edit-page.png
    ...  css=#content

Foldercontents
    Go to  ${PLONE_URL}
    Click element  css=#contentview-folderContents a
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents.png
    ...  css=#content
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-columns.png
    ...  css=#btn-attribute-columns
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-selected.png
    ...  css=#btn-selected-items
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-rearrange.png
    ...  css=#btn-rearrange
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-rearrange.png
    ...  css=#btn-rearrange
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-upload.png
    ...  css=#btn-upload
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-cut.png
    ...  css=#btn-cut
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-copy.png
    ...  css=#btn-copy
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-paste.png
    ...  css=#btn-paste
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-delete.png
    ...  css=#btn-delete
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-rename.png
    ...  css=#btn-rename
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-tags.png
    ...  css=#btn-tags
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-state.png
    ...  css=#btn-workflow
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-properties.png
    ...  css=#btn-properties
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-searchbox.png
    ...  css=#filter

Show display menu
    Go to  ${PLONE_URL}

    Click link  css=#plone-contentmenu-display a

    Wait until element is visible
    ...  css=#plone-contentmenu-display li.plone-toolbar-submenu-header


    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/display-menu.png
            ...  css=#content-header
            ...  css=div.plone-toolbar-container

Reordering
    Go to  ${PLONE_URL}
    Click element  css=#contentview-folderContents a
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/foldercontents-reorder.png
    ...  css=#content

Create sample content for history
    Go to  ${PLONE_URL}

    ${item} =  Create content  type=Document
    ...  id=samplepage  title=Sample Page
    ...  description=The long wait is now over
    ...  text=<p>Our new site is built with Plone.</p>
    Fire transition  ${item}  publish

    Go to  ${PLONE_URL}/samplepage
    Click element  css=#contentview-edit a
    Click element  css=#form-widgets-IDublinCore-title
    Input text  css=#form-widgets-IDublinCore-title  Hurray
    Click element  css=#form-widgets-IVersionable-changeNote
    Input text  css=#form-widgets-IVersionable-changeNote  Title should be Hurray, not Sample Page.
    Click button  css=#form-buttons-save

Show history
    Go to  ${PLONE_URL}/samplepage
    Click link  css=#contentview-history a
    Wait until element is visible
    ...  css=#history-list
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/content-history.png
            ...  css=#content-header
            ...  css=div.plone-toolbar-container

Show portlet management
    Go to  ${PLONE_URL}
    Click link  css=#plone-contentmenu-portletmanager a

    Wait until element is visible
    ...  css=#plone-contentmenu-portletmanager li.plone-toolbar-submenu-header

    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/portlet-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#content-header

Show right portlets
    Go to  ${PLONE_URL}/@@topbar-manage-portlets/plone.footerportlets

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/portlet-footer.png
    ...  css=#content
