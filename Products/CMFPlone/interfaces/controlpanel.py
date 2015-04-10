# -*- coding: utf-8 -*-
from plone.supermodel import model
from Products.CMFPlone import PloneMessageFactory as _  # NOQA
from Products.CMFPlone.utils import validate_json
from basetool import IPloneBaseTool
from plone.locking.interfaces import ILockSettings
from zope import schema
from zope.interface import Interface, implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class IControlPanel(IPloneBaseTool):
    """ Interface for the ControlPanel """

    def registerConfiglet(id, name, action, condition='', permission='',  # NOQA
                          category='Plone', visible=1, appId=None,
                          imageUrl=None, description='', REQUEST=None):
        """ Registration of a Configlet """

    def unregisterConfiglet(id):  # NOQA
        """ unregister Configlet """

    def unregisterApplication(appId):  # NOQA
        """ unregister Application with all configlets """

    def getGroupIds():  # NOQA
        """ list of the group ids """

    def getGroups():  # NOQA
        """ list of groups as dicts with id and title """

    def enumConfiglets(group=None):  # NOQA
        """ lists the Configlets of a group, returns them as dicts by
            calling .getAction() on each of them """


class IEditingSchema(Interface):

    visible_ids = schema.Bool(
        title=_(u"Show 'Short Name' on content?"),
        description=_(
            u"Display and allow users to edit the "
            u"'Short name' content identifiers, which form the "
            u"URL part of a content item's address. Once "
            u"enabled, users will then be able to enable this "
            u"option in their preferences."),
        default=False,
        required=False)

    available_editors = schema.List(
        title=_(u'Available editors'),
        description=_(u"Available editors in the portal."),
        default=['Kupu', 'TinyMCE'],
        value_type=schema.TextLine(),
        required=True
    )

    default_editor = schema.Choice(
        title=_(u'Default editor'),
        description=_(
            u"Select the default wysiwyg "
            u"editor. Users will be able to choose their "
            u"own or select to use the site default."),
        default=u'TinyMCE',
        missing_value=set(),
        vocabulary="plone.app.vocabularies.AvailableEditors",
        required=True)

    ext_editor = schema.Bool(
        title=_(u'Enable External Editor feature'),
        description=_(
            u"Determines if the external editor "
            u"feature is enabled. This feature requires a "
            u"special client-side application installed. The "
            u"users also have to enable this in their "
            u"preferences."),
        default=False,
        required=False)

    enable_link_integrity_checks = schema.Bool(
        title=_(u"Enable link integrity checks"),
        description=_(
            u"Determines if the users should get "
            u"warnings when they delete or move content that "
            u"is linked from inside the site."),
        default=True,
        required=False)

    lock_on_ttw_edit = schema.Bool(
        title=_(u"Enable locking for through-the-web edits"),
        description=_(
            u"Disabling locking here will only "
            u"affect users editing content through the "
            u"Plone web UI.  Content edited via WebDAV "
            u"clients will still be subject to locking."),
        default=True,
        required=False)


class ILanguageSchema(Interface):
    model.fieldset(
        'general',
        label=_(u'General', default=u'General'),
        fields=[
            'default_language',
            'available_languages',
            'use_combined_language_codes',
            'display_flags',
            'always_show_selector'
        ],
    )

    default_language = schema.Choice(
        title=_(u"heading_site_language",
                default=u"Site language"),
        description=_(
            u"description_site_language",
            default=u"The language used for the content and the UI "
                    u"of this site."),
        default='en',
        required=True,
        vocabulary="plone.app.vocabularies.AvailableContentLanguages"
    )

    available_languages = schema.List(
        title=_(u"heading_available_languages",
                default=u"Available languages"),
        description=_(u"description_available_languages",
                      default=u"The languages in which the site should be "
                              u"translatable."),
        required=True,
        default=['en'],
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.AvailableContentLanguages"
        )
    )

    use_combined_language_codes = schema.Bool(
        title=_(
            u'label_allow_combined_language_codes',
            default=u"Show country-specific language variants"
        ),
        description=_(
            u"help_allow_combined_language_codes",
            default=u"Examples: pt-br (Brazilian Portuguese), "
                    u"en-us (American English) etc."
        ),
        default=False,
        required=False
    )

    display_flags = schema.Bool(
        title=_(
            u'label_display_flags',
            default=u"Show language flags"
        ),
        description=_(
            u"help_display_flags",
            default=u""
        ),
        default=False,
        required=False
    )

    always_show_selector = schema.Bool(
        title=_(
            u'label_always_show_selector',
            default=u"Always show language selector"
        ),
        description=_(
            u"help_always_show_selector",
            default=u""
        ),
        default=False,
        required=False
    )

    model.fieldset(
        'negotiation_scheme',
        label=_(u'Negotiation scheme', default=u'Negotiation scheme'),
        fields=[
            'use_content_negotiation',
            'use_path_negotiation',
            'use_cookie_negotiation',
            'authenticated_users_only',
            'set_cookie_always',
            'use_subdomain_negotiation',
            'use_cctld_negotiation',
            'use_request_negotiation',
            ],
        )
    use_content_negotiation = schema.Bool(
        title=_(u"heading_language_of_the_content",
                default=u"Use the language of the content item"),
        description=_(u"description_language_of_the_content",
                      default=u"Use the language of the content item."),
        default=False,
        required=False,
    )

    use_path_negotiation = schema.Bool(
        title=_(
            u"heading_language_codes_in_URL",
            default=u"Use language codes in URL path for manual override"),
        description=_(
            u"description_language_codes_in_URL",
            default=u"Use language codes in URL path for manual override."),
        default=False,
        required=False,
    )

    use_cookie_negotiation = schema.Bool(
        title=_(u"heading_cookie_manual_override",
                default=(u"Use cookie for manual override")),
        description=_(
            u"description_cookie_manual_override",
            default=(u"Required for the language selector viewlet to be rendered.")
        ),
        default=False,
        required=False,
    )

    authenticated_users_only = schema.Bool(
        title=_(u"heading_auth_cookie_manual_override",
                default=u"Authenticated users only"),
        description=_(
            u"description_auth_ookie_manual_override",
            default=(u"Related to Use cookie for manual override")
        ),
        default=False,
        required=False,
    )

    set_cookie_always = schema.Bool(
        title=_(
            u"heading_set_language_cookie_always",
            default=(u"Set the language cookie always")),
        description=_(
            u"description_set_language_cookie_always",
            default=(u"i.e. also when the 'set_language' request parameter is absent")),
        default=False,
        required=False,
        )

    use_subdomain_negotiation = schema.Bool(
        title=_(u"heading_use_subdomain",
                default=u"Use subdomain"),
        description=_(u"description_use_subdomain",
                      default=u"e.g.: de.plone.org"),
        default=False,
        required=False,
        )

    use_cctld_negotiation = schema.Bool(
        title=_(u"heading_top_level_domain",
                default=u"Use top-level domain"),
        description=_(u"description_top_level_domain",
                      default=u"e.g.: www.plone.de"),
        default=False,
        required=False,
        )

    use_request_negotiation = schema.Bool(
        title=_(u"heading_browser_language_request_negotiation",
                default=u"Use browser language request negotiation"),
        description=_(u"description_browser_language_request_negotiation",
                      default=u"Use browser language request negotiation."),
        default=False,
        required=False,
        )


class ITagAttrPair(Interface):
    tags = schema.TextLine(title=u"tags")
    attributes = schema.TextLine(title=u"attributes")


class TagAttrPair(object):

    implements(ITagAttrPair)

    def __init__(self, tags='', attributes=''):
        self.tags = tags
        self.attributes = attributes


class IFilterSchema(Interface):
    """Combined schema for the adapter lookup.
    """

    # class IFilterTagsSchema(Interface):

    disable_filtering = schema.Bool(
        title=_(u'Disable html filtering'),
        description=_(u'Warning, disabling can be potentially dangereous. '
                      u'Only disable if you know what you are doing.'),
        default=False,
        required=False)

    nasty_tags = schema.List(
        title=_(u'Nasty tags'),
        description=_(u"These tags, and their content are completely blocked "
                      "when a page is saved or rendered."),
        default=[u'applet', u'embed', u'object', u'script'],
        value_type=schema.TextLine(),
        required=False)

    stripped_tags = schema.List(
        title=_(u'Stripped tags'),
        description=_(u"These tags are stripped when saving or rendering, "
                      "but any content is preserved."),
        default=[u'font', ],
        value_type=schema.TextLine(),
        required=False)

    custom_tags = schema.List(
        title=_(u'Custom tags'),
        description=_(u"Add tag names here for tags which are not part of "
                      "XHTML but which should be permitted."),
        default=[],
        value_type=schema.TextLine(),
        required=False)

    # class IFilterAttributesSchema(Interface):

    stripped_attributes = schema.List(
        title=_(u'Stripped attributes'),
        description=_(u"These attributes are stripped from any tag when "
                      "saving."),
        default=(u'dir lang valign halign border frame rules cellspacing '
                 'cellpadding bgcolor').split(),
        value_type=schema.TextLine(),
        required=False)

    stripped_combinations = schema.Dict(
        title=_(u'Stripped combinations'),
        description=_(u"These attributes are stripped from those tags when "
                      "saving."),
        key_type=schema.TextLine(title=u"tags"),
        value_type=schema.TextLine(title=u"attributes"),
        default={},
        # XXX replace with value adapter
        # default={'table th td': 'width height', 'other tags': 'other attrs'}
        required=False)

    # class IFilterEditorSchema(Interface):

    style_whitelist = schema.List(
        title=_(u'Permitted properties'),
        description=_(
            u'These CSS properties are allowed in style attributes.'),
        default=u'text-align list-style-type float text-decoration'.split(),
        value_type=schema.TextLine(),
        required=False)

    class_blacklist = schema.List(
        title=_(u'Filtered classes'),
        description=_(u'These class names are not allowed in class '
                      'attributes.'),
        default=[],
        value_type=schema.TextLine(),
        required=False)


class ITinyMCEPatternSchema(Interface):

    relatedItems = schema.Text(
        title=_(u"Related Items vocabulary url"),
        description=u"json:{'vocabularyUrl': '%(portal_url)s/@@getVocabulary?name=plone.app.vocabularies.Catalog'}",  # NOQA
        default=u'json:{"vocabularyUrl": "%(portal_url)s/@@getVocabulary?name=plone.app.vocabularies.Catalog"}',  # NOQA
        required=True)

    rel_upload_path = schema.Text(
        title=_(u"Relative upload path"),
        description=u"@@fileUpload",
        default=u'@@fileUpload',
        required=True)

    folder_url = schema.Text(
        title=_(u"Folder URL"),
        description=u"%(document_base_url)s",
        default=u'%(document_base_url)s',
        required=True)

    linkAttribute = schema.TextLine(
        title=_(u"Link Attribute"),
        description=u"UID",
        default=u'UID',
        required=True)

    prependToScalePart = schema.Text(
        title=_(u"Prepend to Scale Part"),
        description=u'/@@images/image/',
        default=u'/@@images/image/')

    content_css = schema.Text(
        title=_(u"Content CSS URL"),
        description=u'++plone++static/components/tinymce/skins/lightgray/content.min.css')  # NOQA


class ITinyMCELayoutSchema(Interface):
    """This interface defines the layout properties."""

    resizing = schema.Bool(
        title=_(u"Enable resizing the editor window."),
        description=_(u"This option gives you the ability to enable/disable "
                      "resizing the editor window. "
                      "If the editor width is set to a percentage "
                      "only vertical resizing is enabled."),
        default=True,
        required=False)

    autoresize = schema.Bool(
        title=_(u"Enable auto resizing of the editor window."),
        description=_(u"This option gives you the ability to enable/disable "
                      "auto resizing the editor window depending "
                      "on the content."),
        default=False,
        required=False)

    # TODO: add validation to assert % and px in the value
    editor_width = schema.TextLine(
        title=_(u"Editor width"),
        description=_(u"This option gives you the ability to specify the "
                      "width of the editor (like 100% or 400px)."),
        default=u'100%',
        required=False)

    # TODO: add validation to assert % and px in the value
    editor_height = schema.TextLine(
        title=_(u"Editor height"),
        description=_(u"This option gives you the ability to specify the "
                      "height of the editor in pixels. "
                      "If auto resize is enabled this value is used "
                      "as minimum height."),
        default=u'400px',
        required=False)

    contextmenu = schema.Bool(
        title=_(u"Enable contextmenu"),
        description=_(u"This option gives you the ability to enable/disable "
                      "the use of the contextmenu."),
        default=True,
        required=False)

    content_css = schema.TextLine(
        title=_(u"Choose the CSS used in WYSIWYG Editor Area"),
        description=_(u"This option enables you to specify a custom CSS file "
                      "that replaces the theme content CSS. "
                      "This CSS file is the one used within the editor "
                      "(the editable area)."),
        default=u'',
        required=False)

    styles = schema.Text(
        title=_(u"Styles"),
        description=_(u"Enter a list of styles to appear in the style "
                      "pulldown. "
                      "Format is title|tag or title|tag|className, "
                      "one per line."),
        default=u"Heading|h2|\n"
                u"Subheading|h3|\n"
                u"Literal|pre|\n"
                u"Discreet|span|discreet\n"
                u"Pull-quote|blockquote|pullquote\n"
                u"Call-out|p|callout\n"
                u"Highlight|span|visualHighlight\n"
                u"Disc|ul|listTypeDisc\n"
                u"Square|ul|listTypeSquare\n"
                u"Circle|ul|listTypeCircle\n"
                u"Numbers|ol|listTypeDecimal\n"
                u"Lower Alpha|ol|listTypeLowerAlpha\n"
                u"Upper Alpha|ol|listTypeUpperAlpha\n"
                u"Lower Roman|ol|listTypeLowerRoman\n"
                u"Upper Roman|ol|listTypeUpperRoman\n"
                u"Definition term|dt|\n"
                u"Definition description|dd|\n"
                u"Odd row|tr|odd\n"
                u"Even row|tr|even\n"
                u"Heading cell|th|\n"
                u"Page break (print only)|div|pageBreak\n"
                u"Clear floats|div|visualClear",
        required=False)

    formats = schema.Text(
        title=_(u"Formats"),
        description=_(
            u"Enter a JSON-formatted style format configuration. "
            u"A format is for example the style that get applied when "
            u"you press the bold button inside the editor. "
            u"See http://www.tinymce.com/wiki.php/Configuration:formats"),
        constraint=validate_json,
        required=False,
    )

    tablestyles = schema.Text(
        title=_(u"Table styles"),
        description=_(
            u"Enter a list of styles to appear in the table style pulldown. "
            "Format is title|class, one per line."),
        default=u"Subdued grid|plain\n"
                u"Invisible grid|invisible\n"
                u"Fancy listing|listing",
        required=False)


class ITinyMCEToolbarSchema(Interface):
    """This interface defines the toolbar properties."""

    toolbar_width = schema.TextLine(
        title=_(u"Toolbar width"),
        description=_(u"This option gives you the ability to specify the "
                      "width of the toolbar in pixels."),
        default=u"440",
        required=False)

    toolbar_external = schema.Bool(
        title=_(u"Place toolbar on top of the page"),
        description=_(u"This option enables the external toolbar which will "
                      "be placed at the top of the page."),
        default=False,
        required=False)

    toolbar_save = schema.Bool(
        title=_(u"Save"),
        default=True,
        required=False)

    toolbar_cut = schema.Bool(
        title=_(u"Cut"),
        default=False,
        required=False)

    toolbar_copy = schema.Bool(
        title=_(u"Copy"),
        default=False,
        required=False)

    toolbar_paste = schema.Bool(
        title=_(u"Paste"),
        default=False,
        required=False)

    toolbar_pastetext = schema.Bool(
        title=_(u"Paste as Plain Text"),
        default=False,
        required=False)

    toolbar_pasteword = schema.Bool(
        title=_(u"Paste from Word"),
        default=False,
        required=False)

    toolbar_undo = schema.Bool(
        title=_(u"Undo"),
        default=False,
        required=False)

    toolbar_redo = schema.Bool(
        title=_(u"Redo"),
        default=False,
        required=False)

    toolbar_search = schema.Bool(
        title=_(u"Find"),
        default=False,
        required=False)

    toolbar_replace = schema.Bool(
        title=_(u"Find/Replace"),
        default=False,
        required=False)

    toolbar_style = schema.Bool(
        title=_(u"Select Style"),
        default=True,
        required=False)

    toolbar_bold = schema.Bool(
        title=_(u"Bold"),
        default=True,
        required=False)

    toolbar_italic = schema.Bool(
        title=_(u"Italic"),
        default=True,
        required=False)

    toolbar_underline = schema.Bool(
        title=_(u"Underline"),
        default=False,
        required=False)

    toolbar_strikethrough = schema.Bool(
        title=_(u"Strikethrough"),
        default=False,
        required=False)

    toolbar_sub = schema.Bool(
        title=_(u"Subscript"),
        default=False,
        required=False)

    toolbar_sup = schema.Bool(
        title=_(u"Superscript"),
        default=False,
        required=False)

    toolbar_forecolor = schema.Bool(
        title=_(u"Forecolor"),
        default=False,
        required=False)

    toolbar_backcolor = schema.Bool(
        title=_(u"Backcolor"),
        default=False,
        required=False)

    toolbar_justifyleft = schema.Bool(
        title=_(u"Align left"),
        default=True,
        required=False)

    toolbar_justifycenter = schema.Bool(
        title=_(u"Align center"),
        default=True,
        required=False)

    toolbar_justifyright = schema.Bool(
        title=_(u"Align right"),
        default=True,
        required=False)

    toolbar_justifyfull = schema.Bool(
        title=_(u"Align full"),
        default=True,
        required=False)

    toolbar_bullist = schema.Bool(
        title=_(u"Unordered list"),
        default=True,
        required=False)

    toolbar_numlist = schema.Bool(
        title=_(u"Ordered list"),
        default=True,
        required=False)

    toolbar_definitionlist = schema.Bool(
        title=_(u"Definition list"),
        default=True,
        required=False)

    toolbar_outdent = schema.Bool(
        title=_(u"Outdent"),
        default=True,
        required=False)

    toolbar_indent = schema.Bool(
        title=_(u"Indent"),
        default=True,
        required=False)

    toolbar_tablecontrols = schema.Bool(
        title=_(u"Table controls"),
        default=True,
        required=False)

    toolbar_link = schema.Bool(
        title=_(u"Insert/edit link"),
        default=True,
        required=False)

    toolbar_unlink = schema.Bool(
        title=_(u"Unlink"),
        default=True,
        required=False)

    toolbar_anchor = schema.Bool(
        title=_(u"Insert/edit anchor"),
        default=True,
        required=False)

    toolbar_image = schema.Bool(
        title=_(u"Insert/edit image"),
        default=True,
        required=False)

    toolbar_media = schema.Bool(
        title=_(u"Insert/edit media"),
        default=False,
        required=False)

    toolbar_charmap = schema.Bool(
        title=_(u"Insert custom character"),
        default=False,
        required=False)

    toolbar_hr = schema.Bool(
        title=_(u"Insert horizontal ruler"),
        default=False,
        required=False)

    toolbar_advhr = schema.Bool(
        title=_(u"Insert advanced horizontal ruler"),
        default=False,
        required=False)

    toolbar_insertdate = schema.Bool(
        title=_(u"Insert date"),
        default=False,
        required=False)

    toolbar_inserttime = schema.Bool(
        title=_(u"Insert time"),
        default=False,
        required=False)

    toolbar_emotions = schema.Bool(
        title=_(u"Emotions"),
        default=False,
        required=False)

    toolbar_nonbreaking = schema.Bool(
        title=_(u"Insert non-breaking space character"),
        default=False,
        required=False)

    toolbar_pagebreak = schema.Bool(
        title=_(u"Insert page break"),
        default=False,
        required=False)

    toolbar_print = schema.Bool(
        title=_(u"Print"),
        default=False,
        required=False)

    toolbar_preview = schema.Bool(
        title=_(u"Preview"),
        default=False,
        required=False)

    toolbar_spellchecker = schema.Bool(
        title=_(u"Spellchecker"),
        default=False,
        required=False)

    toolbar_removeformat = schema.Bool(
        title=_(u"Remove formatting"),
        default=False,
        required=False)

    toolbar_cleanup = schema.Bool(
        title=_(u"Cleanup messy code"),
        default=False,
        required=False)

    toolbar_visualaid = schema.Bool(
        title=_(u"Toggle guidelines/invisible objects"),
        default=False,
        required=False)

    toolbar_visualchars = schema.Bool(
        title=_(u"Visual control characters on/off"),
        default=False,
        required=False)

    toolbar_attribs = schema.Bool(
        title=_(u"Insert/edit attributes"),
        default=False,
        required=False)

    toolbar_code = schema.Bool(
        title=_(u"Edit HTML Source"),
        default=True,
        required=False)

    toolbar_fullscreen = schema.Bool(
        title=_(u"Toggle fullscreen mode"),
        default=True,
        required=False)

    customtoolbarbuttons = schema.Text(
        title=_(u"Custom Toolbar Buttons"),
        description=_(u"Enter a list of custom toolbar buttons which will be "
                      "loaded in the editor, one per line."),
        default=u"",
        required=False)


class ITinyMCELibrariesSchema(Interface):
    """This interface defines the libraries properties."""

    libraries_spellchecker_choice = schema.Choice(
        title=_(u"Spellchecker plugin to use"),
        description=_(u"This option allows you to choose the spellchecker for "
                      u"TinyMCE. If you want the spellchecker button to be "
                      u"visible, make sure it is enabled in the toolbar "
                      u"settings."),
        missing_value=set(),
        vocabulary=SimpleVocabulary([
            SimpleTerm('browser', 'browser',
                       _(u"Default browser spellchecker")),
            SimpleTerm('iespell', 'iespell',
                       _(u"ieSpell (free for personal use)")),
            SimpleTerm('AtD', 'AtD',
                       _(u"After the deadline (FLOSS)")),
        ]),
        default=u'browser',
        required=False)

    libraries_atd_ignore_strings = schema.Text(
        title=_(u"AtD Ignore strings"),
        description=_(
            'label_atd_ignore_strings',
            default=u"A list of strings which the \"After the Deadline\" "
                    u"spellchecker should ignore. "
                    u"Note: This option is only applicable when the "
                    u"appropriate spellchecker has been chosen above."),
        default=u"Zope\nPlone\nTinyMCE",
        required=False)

    libraries_atd_show_types = schema.Text(
        title=_(u"AtD Error types to show"),
        description=_(
            'help_atderrortypes_to_show',
            default=u"A list of error types which the "
                    u"\"After the Deadline\" spellchecker should check for. "
                    u"By default, all the available error type will be "
                    u"listed here."),
        default=u"Bias Language\nCliches\nComplex Expression\n"
                u"Diacritical Marks\nDouble Negatives\n"
                u"Hidden Verbs\nJargon Language\nPassive voice\n"
                u"Phrases to Avoid\nRedundant Expression",
        required=False)

    libraries_atd_service_url = schema.TextLine(
        title=_(u"AtD Service URL"),
        description=_(
            'help_atd_service_url',
            default=u"The URL of the \"After the Deadline\" grammar and spell "
                    u"checking server. "
                    u"The default value is the public server, "
                    u"but ideally you should download and install your own "
                    u"and specify its address here."),
        required=True,
        default=u"service.afterthedeadline.com",)


class ITinyMCEResourceTypesSchema(Interface):
    """This interface defines the resource types properties."""

    link_using_uids = schema.Bool(
        title=_(u"Link using UIDs"),
        description=_(u"Links to objects on this site can use unique object "
                      "ids so that the links remain valid even if the target "
                      "object is renamed or moved elsewhere on the site."),
        default=True,
        required=False)

    allow_captioned_images = schema.Bool(
        title=_(u"Allow captioned images"),
        description=_(u"Images will be automatically captioned."),
        default=False,
        required=False)

    rooted = schema.Bool(
        title=_(u"Rooted to current object"),
        description=_(u"When enabled the user will be rooted to the current "
                      "object and can't add links and images from other parts "
                      "of the site."),
        default=False,
        required=False)

    containsobjects = schema.Text(
        title=_(u"Contains Objects"),
        description=_(u"Enter a list of content types which can contain other "
                      "objects. Format is one contenttype per line."),
        default=u"Folder\n"
                u"Large Plone Folder\n"
                u"Plone Site",
        required=False)

    containsanchors = schema.Text(
        title=_(u"Contains Anchors"),
        description=_(u"Enter a list of content types which can contain "
                      "anchors. Format is one contenttype per line."),
        default=u"Event\n"
                u"News Item\n"
                u"Document\n"
                u"ATRelativePathCriterion",
        required=False)

    linkable = schema.Text(
        title=_(u"Linkable Objects"),
        description=_(u"Enter a list of content types which can be linked. "
                      "Format is one contenttype per line."),
        required=False)

    imageobjects = schema.Text(
        title=_(u"Image Objects"),
        description=_(u"Enter a list of content types which can be used as "
                      "images. Format is one contenttype per line."),
        default=u"Image",
        required=False)

    plugins = schema.List(
        title=_("label_tinymce_plugins", default=u"Editor Plugins"),
        description=_("help_tinymce_plugins", default=(
            u"Enter a list of custom plugins which will be loaded in the "
            u"editor. Format is pluginname or pluginname|location, one per "
            u"line.")),
        value_type=schema.Choice(vocabulary=SimpleVocabulary([
            SimpleTerm('advhr', 'advhr', u"advhr"),
            SimpleTerm('definitionlist', 'definitionlist', u"definitionlist"),
            SimpleTerm('directionality', 'directionality', u"directionality"),
            SimpleTerm('emotions', 'emotions', u"emotions"),
            SimpleTerm('fullscreen', 'fullscreen', u"fullscreen"),
            SimpleTerm('inlinepopups', 'inlinepopups', u"inlinepopups"),
            SimpleTerm('insertdatetime', 'insertdatetime', u"insertdatetime"),
            SimpleTerm('media', 'media', u"media"),
            SimpleTerm('nonbreaking', 'nonbreaking', u"nonbreaking"),
            SimpleTerm('noneditable', 'noneditable', u"noneditable"),
            SimpleTerm('pagebreak', 'pagebreak', u"pagebreak"),
            SimpleTerm('paste', 'paste', u"paste"),
            SimpleTerm('plonebrowser', 'plonebrowser', u"plonebrowser"),
            SimpleTerm(
                'ploneinlinestyles', 'ploneinlinestyles',
                u"ploneinlinestyles"),
            SimpleTerm('plonestyle', 'plonestyle', u"plonestyle"),
            SimpleTerm('preview', 'preview', u"preview"),
            SimpleTerm('print', 'print', u"print"),
            SimpleTerm('save', 'save', u"save"),
            SimpleTerm('searchreplace', 'searchreplace', u"searchreplace"),
            SimpleTerm('tabfocus', 'tabfocus', u"tabfocus"),
            SimpleTerm('table', 'table', u"table"),
            SimpleTerm('visualchars', 'visualchars', u"visualchars"),
            SimpleTerm('xhtmlxtras', 'xhtmlxtras', u"xhtmlxtras")
        ])),
        default=['advhr', 'definitionlist', 'directionality', 'emotions',
                 'fullscreen', 'inlinepopups', 'insertdatetime', 'media',
                 'nonbreaking', 'noneditable', 'pagebreak', 'paste',
                 'plonebrowser', 'ploneinlinestyles', 'plonestyle', 'preview',
                 'print', 'save', 'searchreplace', 'tabfocus', 'table',
                 'visualchars', 'xhtmlxtras'],
        required=False)

    customplugins = schema.Text(
        title=_(u"Custom Plugins"),
        description=_(u"Enter a list of custom plugins which will be loaded "
                      "in the editor. Format is pluginname or "
                      "pluginname|location, one per line."),
        default=u"plonebrowser",
        required=False)

    entity_encoding = schema.Choice(
        title=_(u"Entity encoding"),
        description=_(
            u"This option controls how entities/characters get processed. "
            "Named: Characters will be converted into named entities "
            "based on the entities option. "
            "Numeric: Characters will be converted into numeric entities. "
            "Raw: All characters will be stored in non-entity form "
            "except these XML default entities: amp lt gt quot"),
        missing_value=set(),
        vocabulary=SimpleVocabulary(
            [SimpleTerm('named', 'named', _(u"Named")),
             SimpleTerm('numeric', 'numeric', _(u"Numeric")),
             SimpleTerm('raw', 'raw', _(u"Raw"))]),
        default=u"raw",
        required=False)


class ITinyMCESchema(
    ITinyMCELayoutSchema,
    ITinyMCEToolbarSchema,
    ITinyMCELibrariesSchema,
    ITinyMCEResourceTypesSchema,
    ITinyMCEPatternSchema
):
    """TinyMCE Schema"""


class IMaintenanceSchema(Interface):

    days = schema.Int(
        title=_(u"Days of object history to keep after packing"),
        description=_(
            u"You should pack your database regularly. This number "
            u"indicates how many days of undo history you want to "
            u"keep. It is unrelated to versioning, so even if you "
            u"pack the database, the history of the content changes "
            u"will be kept. Recommended value is 7 days."
        ),
        default=7,
        required=True
    )


class INavigationSchema(Interface):

    generate_tabs = schema.Bool(
        title=_(u"Automatically generate tabs"),
        description=_(
            u"By default, all items created at the root level will "
            u"add to the global section navigation. You can turn this off "
            u"if you prefer manually constructing this part of the "
            u"navigation."),
        default=True,
        required=False)

    nonfolderish_tabs = schema.Bool(
        title=_(u"Generate tabs for items other than folders."),
        description=_(
            u"By default, any content item in the root of the portal will "
            u"be shown as a global section. If you turn this option off, "
            u"only folders will be shown. This only has an effect if "
            u"'Automatically generate tabs' is enabled."),
        default=True,
        required=False)

    displayed_types = schema.Tuple(
        title=_(u"Displayed content types"),
        description=_(
            u"The content types that should be shown in the navigation and "
            u"site map."),
        required=False,
        default=('Image', 'File', 'Link', 'News Item', 'Folder', 'Document',
                 'Event'),
        value_type=schema.Choice(
            source="plone.app.vocabularies.ReallyUserFriendlyTypes"
        ))

    filter_on_workflow = schema.Bool(
        title=_(u"Filter on workflow state"),
        description=_(
            u"The workflow states that should be shown in the navigation "
            u"tree and the site map."),
        default=False,
        required=False)

    workflow_states_to_show = schema.Tuple(
        required=False,
        default=(),
        value_type=schema.Choice(
            source="plone.app.vocabularies.WorkflowStates"))

    show_excluded_items = schema.Bool(
        title=_(
            u"Show items normally excluded from navigation if viewing their "
            u"children."),
        description=_(
            u"If an item has been excluded from navigation should it be "
            u"shown in navigation when viewing content contained within it "
            u"or within a subfolder."),
        default=True,
        required=False)


class ISearchSchema(Interface):

    enable_livesearch = schema.Bool(
        title=_(u'Enable LiveSearch'),
        description=_(
            u"Enables the LiveSearch feature, which shows live "
            u"results if the browser supports JavaScript."),
        default=True,
        required=True
    )

    types_not_searched = schema.Tuple(
        title=_(u"Define the types to be shown in the site and searched"),
        description=_(
            u"Define the types that should be searched and be "
            u"available in the user facing part of the site. "
            u"Note that if new content types are installed, they "
            u"will be enabled by default unless explicitly turned "
            u"off here or by the relevant installer."
        ),
        required=False,
        default=(
            'ATBooleanCriterion',
            'ATDateCriteria',
            'ATDateRangeCriterion',
            'ATListCriterion',
            'ATPortalTypeCriterion',
            'ATReferenceCriterion',
            'ATSelectionCriterion',
            'ATSimpleIntCriterion',
            'ATSimpleStringCriterion',
            'ATSortCriterion',
            'ChangeSet',
            'Discussion Item',
            'Plone Site',
            'TempFolder',
            'ATCurrentAuthorCriterion',
            'ATPathCriterion',
            'ATRelativePathCriterion',
        ),
        value_type=schema.Choice(
            source="plone.app.vocabularies.PortalTypes"
        ),
    )


class ISecuritySchema(Interface):

    enable_self_reg = schema.Bool(
        title=_(u'Enable self-registration'),
        description=_(
            u"Allows users to register themselves on the site. If "
            u"not selected, only site managers can add new users."),
        default=False,
        required=False)

    enable_user_pwd_choice = schema.Bool(
        title=_(u'Let users select their own passwords'),
        description=_(
            u"If not selected, a URL will be generated and "
            u"e-mailed. Users are instructed to follow the link to "
            u"reach a page where they can change their password and "
            u"complete the registration process; this also verifies "
            u"that they have entered a valid email address."),
        default=False,
        required=False)

    enable_user_folders = schema.Bool(
        title=_(u'Enable User Folders'),
        description=_(
            u"If selected, home folders where users can create "
            u"content will be created when they log in."),
        default=False,
        required=False)

    allow_anon_views_about = schema.Bool(
        title=_(u"Allow anyone to view 'about' information"),
        description=_(
            u"If not selected only logged-in users will be able to "
            u"view information about who created an item and when it "
            u"was modified."),
        default=False,
        required=False)

    use_email_as_login = schema.Bool(
        title=_(u'Use email address as login name'),
        description=_(
            u"Allows users to login with their email address instead "
            u"of specifying a separate login name. This also updates "
            u"the login name of existing users, which may take a "
            u"while on large sites. The login name is saved as "
            u"lower case, but to be userfriendly it does not matter "
            u"which case you use to login. When duplicates are found, "
            u"saving this form will fail. You can use the "
            u"@@migrate-to-emaillogin page to show the duplicates."),
        default=False,
        required=False)

    use_uuid_as_userid = schema.Bool(
        title=_(u'Use UUID user ids'),
        description=_(
            u"Use automatically generated UUIDs as user id for new users. "
            u"When not turned on, the default is to use the same as the "
            u"login name, or when using the email address as login name we "
            u"generate a user id based on the fullname."),
        default=False,
        required=False)


# XXX: Why does ISiteSchema inherit from ILockSettings here ???
class ISiteSchema(ILockSettings):

    site_title = schema.TextLine(
        title=_(u'Site title'),
        description=_(
            u"This shows up in the title bar of "
            u"browsers and in syndication feeds."),
        default=u'Plone site')

    site_logo = schema.ASCII(
        title=_(u"Site Logo"),
        description=_(u"This shows a custom Logo on your Site."),
        required=False,
    )

    exposeDCMetaTags = schema.Bool(
        title=_(u"Expose Dublin Core metadata"),
        description=_(u"Exposes the Dublin Core properties as metatags."),
        default=False,
        required=False)

    enable_sitemap = schema.Bool(
        title=_(u"Expose sitemap.xml.gz"),
        description=_(
            u"Exposes your content as a file "
            u"according to the sitemaps.org standard. You "
            u"can submit this to compliant search engines "
            u"like Google, Yahoo and Microsoft. It allows "
            u"these search engines to more intelligently "
            u"crawl your site."),
        default=False,
        required=False)

    webstats_js = schema.SourceText(
        title=_(u'JavaScript for web statistics support'),
        description=_(
            u"For enabling web statistics support "
            u"from external providers (for e.g. Google "
            u"Analytics). Paste the code snippets provided. "
            u"It will be included in the rendered HTML as "
            u"entered near the end of the page."),
        default=u'',
        required=False)


class IDateAndTimeSchema(Interface):
    """Controlpanel settings for date and time related settings.
    """

    portal_timezone = schema.Choice(
        title=_(u"Portal default timezone"),
        description=_(
            u"help_portal_timezone",
            default=u"The timezone setting of the portal. Users can set "
                    u"their own timezone, if available timezones are "
                    u"defined."),
        required=True,
        default=None,
        vocabulary="plone.app.vocabularies.CommonTimezones")

    available_timezones = schema.List(
        title=_(u"Available timezones"),
        description=_(
            u"help_available_timezones",
            default=u"The timezones, which should be available for the "
                    u"portal. Can be set for users and events"),
        required=False,
        default=[],
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.Timezones"))

    first_weekday = schema.Choice(
        title=_(u'label_first_weekday', default=u'First Weekday'),
        description=_(
            u'help_first_weekday',
            default=u'First day in the Week.'),
        required=True,
        default=None,
        vocabulary="plone.app.vocabularies.Weekdays")


class ITypesSchema(Interface):
    """
    """


class IMailSchema(Interface):

    smtp_host = schema.TextLine(
        title=_(
            u'label_smtp_server',
            default=u'SMTP server'),
        description=_(
            u"help_smtp_server",
            default=u"The address of your local "
                    u"SMTP (outgoing e-mail) server. Usually "
                    u"'localhost', unless you use an "
                    u"external server to send e-mail."),
        default=u'localhost',
        required=True)

    smtp_port = schema.Int(
        title=_(u'label_smtp_port',
                default=u'SMTP port'),
        description=_(u"help_smtp_port",
                      default=u"The port of your local SMTP "
                              u"(outgoing e-mail) server. Usually '25'."),
        default=25,
        required=True)

    smtp_userid = schema.TextLine(
        title=_(
            u'label_smtp_userid',
            default=u'ESMTP username'),
        description=_(
            u"help_smtp_userid",
            default=u"Username for authentication "
                    u"to your e-mail server. Not required "
                    u"unless you are using ESMTP."),
        default=None,
        required=False)

    smtp_pass = schema.Password(
        title=_(
            u'label_smtp_pass',
            default=u'ESMTP password'),
        description=_(
            u"help_smtp_pass",
            default=u"The password for the ESMTP "
                    u"user account."),
        default=None,
        required=False)

    email_from_name = schema.TextLine(
        title=_(u"Site 'From' name"),
        description=_(
            u"Plone generates e-mail using "
            u"this name as the e-mail "
            u"sender."),
        default=None,
        required=True)

    email_from_address = schema.ASCII(
        title=_(u"Site 'From' address"),
        description=_(
            u"Plone generates e-mail using "
            u"this address as the e-mail "
            u"return address. It is also "
            u"used as the destination "
            u"address for the site-wide "
            u"contact form and the 'Send test "
            u"e-mail' feature."),
        default=None,
        required=True)


class IMarkupSchema(Interface):

    default_type = schema.Choice(
        title=_(u'Default format'),
        description=_(
            u"Select the default format of textfields for newly "
            u"created content objects."
        ),
        default=u'text/html',
        vocabulary="plone.app.vocabularies.AllowableContentTypes",
        required=True
    )

    allowed_types = schema.Tuple(
        title=_(u'Alternative formats'),
        description=_(
            u"Select which formats are available for users as "
            u"alternative to the default format. Note that if new "
            u"formats are installed, they will be enabled for text "
            u"fields by default unless explicitly turned off here "
            u"or by the relevant installer."
        ),
        required=True,
        default=('text/html', 'text/x-web-textile'),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.AllowableContentTypes"
        )
    )


class IUserGroupsSettingsSchema(Interface):

    many_groups = schema.Bool(
        title=_(u'Many groups?'),
        description=_(
            u"Determines if your Plone is optimized "
            u"for small or large sites. In environments with a "
            u"lot of groups it can be very slow or impossible "
            u"to build a list all groups. This option tunes the "
            u"user interface and behaviour of Plone for this "
            u"case by allowing you to search for groups instead "
            u"of listing all of them."),
        default=False
    )

    many_users = schema.Bool(
        title=_(u'Many users?'),
        description=_(
            u"Determines if your Plone is optimized "
            u"for small or large sites. In environments with a "
            u"lot of users it can be very slow or impossible to "
            u"build a list all users. This option tunes the user "
            u"interface and behaviour of Plone for this case by "
            u"allowing you to search for users instead of "
            u"listing all of them."),
        default=False
    )
