*** Settings ***

Resource  common.robot

Suite Setup  Common Suite Setup
Suite Teardown  Common Suite Teardown

*** Variables ***

@{DIMENSIONS}  1280  1600
@{CONFIGURE_PACKAGES}  plone.app.caching
@{APPLY_PROFILES}  plone.app.contenttypes:plone-content  plone.app.caching:default


*** Keywords ***

Highlight field
    [Arguments]  ${locator}
    Update element style  ${locator}  padding  0.5em
    Highlight  ${locator}

*** Test Cases ***

Show Add-ons setup screen
    Go to  ${PLONE_URL}/prefs_install_products_form
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/addon-setup.png
    ...  css=#content

Show caching setup screen
    Go to  ${PLONE_URL}/@@caching-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/caching-setup.png
    ...  css=#content

Show Configuration Registry screen
    Go to  ${PLONE_URL}/portal_registry
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/configuration-registry.png
    ...  css=#content

Show Content setup screen
    Go to  ${PLONE_URL}/@@content-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/content-setup.png
    ...  css=#content

    Click element  type_id

    Select From List  name=type_id  Document

    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/content-document.png
    ...  css=#content

Show Date setup screen
    Go to  ${PLONE_URL}/@@dateandtime-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/date-setup.png
    ...  css=#content

Show Dexterity setup screen
    Go to  ${PLONE_URL}/@@dexterity-types
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/dexterity-setup.png
    ...  css=#content

Show Discussion setup screen
    Go to  ${PLONE_URL}/@@discussion-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/discussion-setup.png
    ...  css=#content

Show Editing setup screen
    Go to  ${PLONE_URL}/@@editing-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/editing-setup.png
    ...  css=#content

Show Error log setup screen
    Go to  ${PLONE_URL}/prefs_error_log_form
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/errorlog-setup.png
    ...  css=#content

Show HTML filter setup screen
    Go to  ${PLONE_URL}/@@filter-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/filter-setup.png
    ...  css=#content

Show Image handling setup screen
    Go to  ${PLONE_URL}/@@imaging-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/imaging-setup.png
    ...  css=#content

Show Site setup overview screen
    Go to  ${PLONE_URL}/@@overview-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/site-overview.png
    ...  css=#content

Show Language setup screen
    Go to  ${PLONE_URL}/@@language-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/language-setup.png
    ...  css=#content

    Click link  autotoc-item-autotoc-1
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/language-negotiation.png
    ...  css=#content

Show Mail setup screen
    Go to  ${PLONE_URL}/@@mail-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/mail-setup.png
    ...  css=#content

Show ZODB maintenance setup screen
    Go to  ${PLONE_URL}/@@maintenance-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/zodb-setup.png
    ...  css=#content

Show Markup setup screen
    Go to  ${PLONE_URL}/@@markup-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/markup-setup.png
    ...  css=#content

Show Navigation setup screen
    Go to  ${PLONE_URL}/@@navigation-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/navigation-setup.png
    ...  css=#content

Show Resource Registry screen
    Go to  ${PLONE_URL}/@@resourceregistry-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/resource-registry.png
    ...  css=#content
    Click link  Less Variables
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/less-variables.png
    ...  css=#content

Show Search setup screen
    Go to  ${PLONE_URL}/@@search-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/search-setup.png
    ...  css=#content

Show Security setup screen
    Go to  ${PLONE_URL}/@@security-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/security-setup.png
    ...  css=#content

Show Site setup screen
    Go to  ${PLONE_URL}/@@site-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/site-setup.png
    ...  css=#content

Show socialmedia setup screen
    Go to  ${PLONE_URL}/@@social-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/social-setup.png
    ...  css=#content

Show Syndication setup screen
    Go to  ${PLONE_URL}/@@syndication-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/syndication-setup.png
    ...  css=#content

Show Theming setup screen
    Go to  ${PLONE_URL}/@@theming-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/theme-setup.png
    ...  css=#content

Show Tinymce setup screen
    Go to  ${PLONE_URL}/@@tinymce-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/tinymce-setup.png
    ...  css=#content

Show Users setup screen
    Go to  ${PLONE_URL}/@@usergroup-userprefs
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/users-setup.png
    ...  css=#content

    Go to  ${PLONE_URL}/@@usergroup-groupprefs
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/groups-setup.png
    ...  css=#content
    Go to  ${PLONE_URL}/@@usergroup-controlpanel
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/users-settings.png
    ...  css=#content
    Go to  ${PLONE_URL}/@@member-fields
    Capture and crop page screenshot
    ...  ${CURDIR}/_robot/users-fields.png
    ...  css=#content

Changing the logo
    Go to  ${PLONE_URL}/@@site-controlpanel
    Highlight field  css=#formfield-form-widgets-site_logo
    Capture and crop page screenshot
    ...    ${CURDIR}/_robot/change-logo-in-site-control-panel.png
    ...    css=#content
    ...    css=#formfield-form-widgets-site_logo