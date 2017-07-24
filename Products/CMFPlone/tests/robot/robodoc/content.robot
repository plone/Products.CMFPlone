*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown



*** Test Cases ***

Show add collection menu
    Go to  ${PLONE_URL}
    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories
    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  collection
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-collections_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul


Select collection criteria
    Go to  ${PLONE_URL}/++add++Collection
    Click element  css=div.querystring-criteria-index a
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/collection-criteria.png
    ...  css=div.select2-drop-active

Show add new event menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  event
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-events_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Show new event add form
    Page should contain element  event
    Click link  event

    Wait until element is visible
    ...  css=#mceu_16-body
    Wait until element is visible
    ...  id=portal-footer
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-events_add-form.png
    ...  id=content

Show add files menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories
    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  file
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-files_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Show new file add form
    Page should contain element  file
    Click link  file

    Wait until element is visible
    ...  css=#form-widgets-title

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-files_add-form.png
    ...  css=#content

Show add new folder menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  folder
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-folders_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Show new folder add form
    Page should contain element  folder
    Click link  folder

    Wait until element is visible
    ...  css=#form-widgets-IDublinCore-title

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-folders_add-form.png
    ...  css=#content

Show add new image menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  image
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-images_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Show new image edit form
    Page should contain element  image
    Click link  image

    Wait until element is visible
    ...  css=#form-widgets-title

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-images_add-form.png
    ...  css=#content

*** Test Cases ***

Show add new link menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  link
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-links_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

*** Test Cases ***

Show new link add form
    Page should contain element  link
    Click link  link

    Wait until element is visible
    ...  css=#form-widgets-IDublinCore-title

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-links_add-form.png
    ...  css=#content

Show add new content menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  document
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-content_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Show add new news-item menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  news-item
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-news-items_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Show new news-item edit form
    Page should contain element  news-item
    Click link  news-item

    Wait until element is visible
    ...  css=#mceu_16-body

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-news-items_add-form.png
    ...  css=#content

Show add new page menu
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  document
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-pages_add-menu.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Show new page edit form
    Page should contain element  document
    Click link  document

    Wait until element is visible
    ...  css=#mceu_16-body

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/adding-pages_add-form.png
    ...  css=#content

Show Content restrictions
    Go to  ${PLONE_URL}/news

    Click link  css=#plone-contentmenu-factories a

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Mouse over  plone-contentmenu-settings
    Update element style  portal-footer  display  none

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/show-restrictions.png
    ...  css=div.plone-toolbar-container
    ...  css=#plone-contentmenu-factories ul

Menu restrictions
    Go to  ${PLONE_URL}/news/folder_constraintypes_form

    Click element  form-widgets-constrain_types_mode


    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/menu-restrictions.png
    ...  css=#main-container

Show basic content properties tab
    Go to  ${PLONE_URL}

    Wait until element is visible
    ...  css=span.icon-plone-contentmenu-factories
    Click element  css=span.icon-plone-contentmenu-factories

    Wait until element is visible
    ...  css=#plone-contentmenu-factories li.plone-toolbar-submenu-header

    Page should contain element  document
    Click link  document
    Update element style  portal-footer  display  none

    Wait until element is visible
    ...  css=#form-widgets-IDublinCore-title

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/basicpropertiestabs.png
    ...  css=nav.autotoc-nav

Show edit page categorization
    Click link  Categorization

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/editpagecategorization.png
    ...  css=#content-core

Show content dates settings
    Click link  Dates

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/datessettings.png
    ...  css=#content-core

Show content ownershippanel
    Click link  Ownership

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/ownershippanel.png
    ...  css=#content-core

Show content settingspanel
    Click link  Settings

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/settingspanel.png
    ...  css=#content-core