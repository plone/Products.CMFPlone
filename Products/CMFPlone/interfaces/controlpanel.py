# -*- coding: utf-8 -*-
import json

from Products.CMFPlone import PloneMessageFactory as _  # NOQA
from Products.CMFPlone.utils import validate_json
from basetool import IPloneBaseTool
from plone.supermodel import model
from zope import schema
from zope.interface import Interface, implements
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


ROBOTS_TXT = u"""Sitemap: {portal_url}/sitemap.xml.gz

# Define access-restrictions for robots/spiders
# http://www.robotstxt.org/wc/norobots.html



# By default we allow robots to access all areas of our site
# already accessible to anonymous users

User-agent: *
Disallow:



# Add Googlebot-specific syntax extension to exclude forms
# that are repeated for each piece of content in the site
# the wildcard is only supported by Googlebot
# http://www.google.com/support/webmasters/bin/answer.py?answer=40367&ctx=sibling

User-Agent: Googlebot
Disallow: /*?
Disallow: /*atct_album_view$
Disallow: /*folder_factories$
Disallow: /*folder_summary_view$
Disallow: /*login_form$
Disallow: /*mail_password_form$
Disallow: /*search
Disallow: /*search_rss$
Disallow: /*sendto_form$
Disallow: /*summary_view$
Disallow: /*thumbnail_view$
Disallow: /*view$
"""


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

    available_editors = schema.List(
        title=_(u'Available editors'),
        description=_(u"Available editors in the portal."),
        default=['TinyMCE', 'None'],
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
        label=_(u'General'),
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
        default=True,
        required=False
    )

    display_flags = schema.Bool(
        title=_(
            u'label_display_flags',
            default=u"Show language flags"
        ),
        description=u"",
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
        default=[u'style', u'object', u'embed', u'applet', u'script', u'meta'],
        value_type=schema.TextLine(),
        missing_value=[],
        required=False)

    stripped_tags = schema.List(
        title=_(u'Stripped tags'),
        description=_(u"These tags are stripped when saving or rendering, "
                      "but any content is preserved."),
        default=[u'font', ],
        value_type=schema.TextLine(),
        missing_value=[],
        required=False)

    custom_tags = schema.List(
        title=_(u'Custom tags'),
        description=_(u"Add tag names here for tags which are not part of "
                      "XHTML but which should be permitted."),
        default=[],
        value_type=schema.TextLine(),
        missing_value=[],
        required=False)

    # class IFilterAttributesSchema(Interface):

    stripped_attributes = schema.List(
        title=_(u'Stripped attributes'),
        description=_(u"These attributes are stripped from any tag when "
                      "saving."),
        default=(u'dir lang valign halign border frame rules cellspacing '
                 'cellpadding bgcolor').split(),
        value_type=schema.TextLine(),
        missing_value=[],
        required=False)

    stripped_combinations = schema.Dict(
        title=_(u'Stripped combinations'),
        description=_(u"These attributes are stripped from those tags when "
                      "saving."),
        key_type=schema.TextLine(title=u"tags"),
        value_type=schema.TextLine(title=u"attributes"),
        default={'table th td': 'width height'},
        missing_value={},
        required=False)

    # class IFilterEditorSchema(Interface):

    style_whitelist = schema.List(
        title=_(u'Permitted properties'),
        description=_(
            u'These CSS properties are allowed in style attributes.'),
        default=u'text-align list-style-type float padding-left text-decoration'.split(),
        value_type=schema.TextLine(),
        missing_value=[],
        required=False)

    class_blacklist = schema.List(
        title=_(u'Filtered classes'),
        description=_(u'These class names are not allowed in class '
                      'attributes.'),
        default=[],
        missing_value=[],
        value_type=schema.TextLine(),
        required=False)


class ITinyMCELayoutSchema(Interface):
    """This interface defines the layout properties."""

    resizing = schema.Bool(
        title=_(u"Enable resizing the editor window."),
        description=_(u"This option gives you the ability to enable/disable "
                      "resizing the editor window. "),
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
        default=None,
        required=False)

    # TODO: add validation to assert % and px in the value
    editor_height = schema.TextLine(
        title=_(u"Editor height"),
        description=_(u"This option gives you the ability to specify the "
                      "height of the editor in pixels. "
                      "If auto resize is enabled this value is used "
                      "as minimum height."),
        default=None,
        required=False)

    content_css = schema.List(
        title=_(u"Choose the CSS used in WYSIWYG Editor Area"),
        description=_(u"This option enables you to specify a custom CSS file "
                      "that provides content CSS. "
                      "This CSS file is the one used within the editor "
                      "(the editable area). In addition to what is listed here, "
                      "the plone bundle CSS and diazo themes using the "
                      "tinymce-content-css setting are also added."),
        value_type=schema.TextLine(),
        default=[
            u'++plone++static/components/tinymce/skins/lightgray/content.min.css',
        ],
        required=False)

    header_styles = schema.List(
        title=_(u"Header styles"),
        description=_('Name|tag'),
        value_type=schema.TextLine(),
        default=[
            u'Header 1|h1',
            u"Header 2|h2",
            u"Header 3|h3",
            u"Header 4|h4",
            u"Header 5|h5",
            u"Header 6|h6"
        ])

    inline_styles = schema.List(
        title=_(u"Inline styles"),
        description=_('Name|format|icon'),
        value_type=schema.TextLine(),
        default=[
            u"Bold|bold|bold",
            u"Italic|italic|italic",
            u"Underline|underline|underline",
            u"Strikethrough|strikethrough|strikethrough",
            u"Superscript|superscript|superscript",
            u"Subscript|subscript|subscript",
            u"Code|code|code"])

    block_styles = schema.List(
        title=_(u"Block styles"),
        description=_('Name|format'),
        value_type=schema.TextLine(),
        default=[
            u"Paragraph|p",
            u"Blockquote|blockquote",
            u"Div|div",
            u"Pre|pre"])

    alignment_styles = schema.List(
        title=_(u"Alignment styles"),
        description=_('Name|format|icon'),
        value_type=schema.TextLine(),
        default=[
            u"Left|alignleft|alignleft",
            u"Center|aligncenter|aligncenter",
            u"Right|alignright|alignright",
            u"Justify|alignjustify|alignjustify"])

    table_styles = schema.List(
        title=_(u"Table styles"),
        description=_('Name|class'),
        value_type=schema.TextLine(),
        default=[
            u"Listing|listing"
        ])

    formats = schema.Text(
        title=_(u"Formats"),
        description=_(
            u"Enter a JSON-formatted style format configuration. "
            u"A format is for example the style that get applied when "
            u"you press the bold button inside the editor. "
            u"See http://www.tinymce.com/wiki.php/Configuration:formats"),
        constraint=validate_json,
        default=json.dumps({
            'discreet': {'inline': 'span', 'classes': 'discreet'},
            'clearfix': {'block': 'div', 'classes': 'clearfix'}
        }, indent=4).decode('utf8'),
        required=True,
    )


class ITinyMCEPluginSchema(Interface):
    """This interface defines the toolbar properties."""

    plugins = schema.List(
        title=_("label_tinymce_plugins", default=u"Editor plugins"),
        description=_("help_tinymce_plugins", default=(
            u"Select plugins to include with tinymce")),
        value_type=schema.Choice(vocabulary=SimpleVocabulary([
            SimpleTerm('advlist', 'advlist', u"advlist"),
            SimpleTerm('anchor', 'anchor', u"anchor"),
            SimpleTerm('autosave', 'autosave', u"autosave"),
            SimpleTerm('charmap', 'charmap', u"charmap"),
            SimpleTerm('code', 'code', u"code"),
            SimpleTerm('colorpicker', 'colorpicker', u"colorpicker"),
            SimpleTerm('contextmenu', 'contextmenu', u"contextmenu"),
            SimpleTerm('directionality', 'directionality', u"directionality"),
            SimpleTerm('emoticons', 'emoticons', u"emoticons"),
            SimpleTerm('fullpage', 'fullpage', u"fullpage"),
            SimpleTerm('fullscreen', 'fullscreen', u"fullscreen"),
            SimpleTerm('hr', 'hr', u"hr"),
            SimpleTerm('insertdatetime', 'insertdatetime', u"insertdatetime"),
            SimpleTerm('layer', 'layer', u"layer"),
            SimpleTerm('lists', 'lists', u"lists"),
            SimpleTerm('media', 'media', u"media"),
            SimpleTerm('nonbreaking', 'nonbreaking', u"nonbreaking"),
            SimpleTerm('noneditable', 'noneditable', u"noneditable"),
            SimpleTerm('pagebreak', 'pagebreak', u"pagebreak"),
            SimpleTerm('paste', 'paste', u"paste"),
            SimpleTerm('preview', 'preview', u"preview"),
            SimpleTerm('print', 'print', u"print"),
            # XXX disable save button since it is not implemeneted
            # SimpleTerm('save', 'save', u"save"),
            SimpleTerm('searchreplace', 'searchreplace', u"searchreplace"),
            SimpleTerm('tabfocus', 'tabfocus', u"tabfocus"),
            SimpleTerm('table', 'table', u"table"),
            SimpleTerm('textcolor', 'textcolor', u"textcolor"),
            SimpleTerm('textpattern', 'textpattern', u"textpattern"),
            SimpleTerm('visualblocks', 'visualblocks', u"visualblocks"),
            SimpleTerm('visualchars', 'visualchars', u"visualchars"),
            SimpleTerm('wordcount', 'wordcount', u"wordcount")
        ])),
        default=['advlist', 'fullscreen', 'hr', 'lists', 'media',
                 'nonbreaking', 'noneditable', 'pagebreak', 'paste', 'preview',
                 'print', 'searchreplace', 'tabfocus', 'table',
                 'visualchars', 'wordcount', 'code'],
        required=False)

    menubar = schema.List(
        title=_("label_tinymce_menubar", default=u"Menubar"),
        description=_("help_tinymce_menubar", default=(
            u"Enter what items you would like in the menu bar.")),
        required=True,
        value_type=schema.TextLine(),
        default=[
            u'edit', u'table', u'format',
            u'tools' u'view', u'insert'])

    menu = schema.Text(
        title=_('label_tinymce_menu', 'Menu'),
        description=_('hint_tinymce_menu',
                      default='JSON formatted Menu configuration.'),
        default=json.dumps({
            'edit': {
                'title': 'Edit',
                'items': 'undo redo | cut copy paste pastetext | '
                         'searchreplace textpattern selectall | textcolor'},
            'insert': {'title': 'Insert', 'items': 'link media | template hr'},
            'view': {'title': 'View', 'items': 'visualaid visualchars visualblocks preview '
                                               'fullpage fullscreen'},
            'format': {'title': 'Format',
                       'items': 'bold italic underline strikethrough '
                                'superscript subscript | formats | removeformat'},
            'table': {'title': 'Table', 'items': 'inserttable tableprops deletetable '
                                                 '| cell row column'},
            'tools': {
                'title': 'Tools',
                'items': 'spellchecker charmap emoticons insertdatetime layer code'}
        }, indent=4).decode('utf8')
    )

    templates = schema.Text(
        title=_("label_tinymce_templates", default=u"Templates"),
        description=_("help_tinymce_templates", default=(
            u"Enter the list of templates in json format \
                http://www.tinymce.com/wiki.php/Plugin:template")),
        required=False,
        default=u"")

    toolbar = schema.Text(
        title=_("label_tinymce_toolbar", default=u"Toolbar"),
        description=_("help_tinymce_toolbar", default=(
            u"Enter how you would like the toolbar items to list.")),
        required=True,
        default=u'ltr rtl | undo redo | styleselect | bold italic | '
                u'alignleft aligncenter alignright alignjustify | '
                u'bullist numlist outdent indent | '
                u'unlink plonelink ploneimage')

    custom_plugins = schema.List(
        title=_(u"Custom plugins"),
        description=_(u"Enter a list of custom plugins which will be loaded "
                      "in the editor. Format is "
                      "pluginname|location, one per line."),
        required=False,
        value_type=schema.TextLine(),
        default=[])

    custom_buttons = schema.List(
        title=_(u"Custom buttons"),
        description=_(u"Enter a list of custom buttons which will be added to toolbar"),
        required=False,
        value_type=schema.TextLine(),
        default=[])
ITinyMCELibrariesSchema = ITinyMCEPluginSchema  # bw compat


class ITinyMCESpellCheckerSchema(Interface):
    """This interface defines the libraries properties."""

    libraries_spellchecker_choice = schema.Choice(
        title=_(u"Spellchecker plugin to use"),
        description=_(u"This option allows you to choose the spellchecker for "
                      u"TinyMCE."),
        missing_value=set(),
        vocabulary=SimpleVocabulary([
            SimpleTerm('browser', 'browser',
                       _(u"Default browser spellchecker")),
            SimpleTerm('AtD', 'AtD',
                       _(u"After the deadline (FLOSS)")),
        ]),
        default=u'browser',
        required=False)

    libraries_atd_ignore_strings = schema.List(
        title=_(u"AtD ignore strings"),
        description=_(
            'label_atd_ignore_strings',
            default=u"A list of strings which the \"After the Deadline\" "
                    u"spellchecker should ignore. "
                    u"Note: This option is only applicable when the "
                    u"appropriate spellchecker has been chosen above."),
        default=[
            u"Zope",
            u"Plone",
            u"TinyMCE"],
        value_type=schema.TextLine(),
        required=False)

    libraries_atd_show_types = schema.List(
        title=_(u"AtD error types to show"),
        description=_(
            'help_atderrortypes_to_show',
            default=u"A list of error types which the "
                    u"\"After the Deadline\" spellchecker should check for. "
                    u"By default, all the available error type will be "
                    u"listed here."),
        value_type=schema.TextLine(),
        default=[
            u"Bias Language",
            u"Cliches",
            u"Complex Expression",
            u"Diacritical Marks",
            u"Double Negatives",
            u"Hidden Verbs",
            u"Jargon Language",
            u"Passive voice",
            u"Phrases to Avoid",
            u"Redundant Expression"],
        required=False)

    libraries_atd_service_url = schema.TextLine(
        title=_(u"AtD service URL"),
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

    # XXX Not implemented in new tinymce version. Need to decide about this
    # rooted = schema.Bool(
    #    title=_(u"Rooted to current object"),
    #    description=_(u"When enabled the user will be rooted to the current "
    #                  "object and can't add links and images from other parts "
    #                  "of the site."),
    #    default=False,
    #    required=False)

    contains_objects = schema.List(
        title=_(u"Contains objects"),
        description=_(u"Enter a list of content types which can contain other "
                      "objects. Format is one contenttype per line."),
        value_type=schema.TextLine(),
        default=[
            u"Folder",
            u"Large Plone Folder",
            u"Plone Site"],
        required=False)

    # XXX not implements
    # containsanchors = schema.Text(
    #    title=_(u"Contains Anchors"),
    #    description=_(u"Enter a list of content types which can contain "
    #                  "anchors. Format is one contenttype per line."),
    #    default=u"Event\n"
    #            u"News Item\n"
    #            u"Document\n"
    #            u"ATRelativePathCriterion",
    #    required=False)

    # XXX do we still want this?
    # seems like it could be really annoying for users
    # creating new types.
    # linkable = schema.Text(
    #    title=_(u"Linkable Objects"),
    #    description=_(u"Enter a list of content types which can be linked. "
    #                  "Format is one contenttype per line."),
    #    required=False)

    image_objects = schema.List(
        title=_(u"Image objects"),
        description=_(u"Enter a list of content types which can be used as "
                      "images. Format is one contenttype per line."),
        default=[u"Image"],
        value_type=schema.TextLine(),
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
    ITinyMCEPluginSchema,
    ITinyMCESpellCheckerSchema,
    ITinyMCEResourceTypesSchema
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
        min=0,
        required=True
    )


class INavigationSchema(Interface):

    generate_tabs = schema.Bool(
        title=_(u"Automatically generate tabs"),
        description=_(
            u"By default, all items created at the root level will "
            u"appear as tabs. You can turn this off if you prefer manually "
            u"constructing this part of the navigation."),
        default=True,
        required=False)

    nonfolderish_tabs = schema.Bool(
        title=_(u"Generate tabs for items other than folders."),
        description=_(
            u"By default, any content item in the root of the portal will "
            u"appear as a tab. If you turn this option off, only folders "
            u"will be shown. This only has an effect if 'Automatically "
            u"generate tabs' is enabled."),
        default=True,
        required=False)

    sort_tabs_on = schema.Choice(
        title=_(u"Sort tabs on"),
        description=_(
            u"Index used to sort the tabs"
        ),
        required=True,
        default=u'getObjPositionInParent',
        vocabulary=SimpleVocabulary([
            # there is no vocabulary of sortable indexes by now, so hard code
            # some options here
            SimpleTerm(
                'getObjPositionInParent',
                'getObjPositionInParent',
                _(u'Position in Parent')
            ),
            SimpleTerm(
                'sortable_title',
                'sortable_title',
                _(u'Title')
            ),
            SimpleTerm(
                'getId',
                'getId',
                _(u'Short Name (ID)')
            ),
        ]),
    )
    sort_tabs_reversed = schema.Bool(
        title=_(u"Reversed sort order for tabs."),
        description=_(
            u"Sort tabs in descending."),
        default=False,
        required=False)

    displayed_types = schema.Tuple(
        title=_(u"Displayed content types"),
        description=_(
            u"The content types that should be shown in the navigation and "
            u"site map."),
        required=False,
        default=(
            'Image',
            'File',
            'Link',
            'News Item',
            'Folder',
            'Document',
            'Event'
        ),
        value_type=schema.Choice(
            source="plone.app.vocabularies.ReallyUserFriendlyTypes"
        ))

    filter_on_workflow = schema.Bool(
        title=_(u"Filter on workflow state"),
        description=_(
            u"The workflow states that should be shown in the navigation "
            u"and the site map."),
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

    root = schema.TextLine(
        title=_(
            u"Root"),
        description=_(
            u"Path to be used as navigation root, relative to Plone site root."
            u"Starts with '/'"
        ),
        default=u'/',
        required=True
    )

    sitemap_depth = schema.Int(
        title=_(u"Sitemap depth"),
        description=_(u"Number of folder levels to show in the site map."),
        default=3,
        required=True
    )

    parent_types_not_to_query = schema.List(
        title=_(u"Hide children of these types"),
        description=_(u"Hide content inside the following types in Navigation."),
        default=[u'TempFolder'],
        value_type=schema.TextLine(),
        required=False,
    )


class ISearchSchema(Interface):

    enable_livesearch = schema.Bool(
        title=_(u'Enable LiveSearch'),
        description=_(
            u"Enables the LiveSearch feature, which shows live "
            u"results if the browser supports JavaScript."),
        default=True,
        required=False
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
            'Discussion Item',
            'Plone Site',
            'TempFolder',
        ),
        value_type=schema.Choice(
            source="plone.app.vocabularies.PortalTypes"
        ),
    )

    search_results_description_length = schema.Int(
        title=_(u"Crop the item description in search result listings "
                u"after a number of characters."),
        required=False,
        default=160,
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


class ISiteSchema(Interface):

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

    display_publication_date_in_byline = schema.Bool(
        title=_(u'Display publication date'),
        description=_(u'Show the date a content item was published in the byline.'),
        default=False,
        required=False)

    icon_visibility = schema.Choice(
        title=_(u'Icon visibility'),
        description=_(u'Show icons in listings'),
        default=u'enabled',
        vocabulary=SimpleVocabulary([
            SimpleTerm('false', 'false', _(u'Never')),
            SimpleTerm('enabled', 'enabled', _(u'Always')),
            SimpleTerm('authenticated', 'authenticated',
                       _('For authenticated users only'))]),
        required=True)

    toolbar_position = schema.Choice(
        title=_(u'Position where the toolbar is displayed'),
        description=_(
            u"It can be in the side vertical mode "
            u"or in the top horizontal mode"),
        default=u'side',
        vocabulary=SimpleVocabulary([
            SimpleTerm('side', 'side', _(u"Side")),
            SimpleTerm('top', 'top', _(u"Top"))]),
        required=True)

    toolbar_logo = schema.TextLine(
        title=_(u"Site based relative url for toolbar logo"),
        description=_(
            u"This must be a relative url to portal root site. "
            u"By default its /++plone++static/plone-toolbarlogo.svg"),
        default=u'/++plone++static/plone-toolbarlogo.svg',
        required=False,
    )

    robots_txt = schema.SourceText(
        title=_("robots.txt"),
        description=_(
            u"help_robots_txt",
            default=u"robots.txt is read by search-engines to "
                    u"determine how to index your site. "
                    u"For details see <a href='http://www.robotstxt.org'>"
                    u"http://www.robotstxt.org</a>. "
                    u"'{portal_url}' is replaced by the sites url."),
        default=ROBOTS_TXT,
        required=False,
    )

    default_page = schema.List(
        title=_(u'Default page ids'),
        description=_(
            u"Select which ids can act as fallback default pages for",
            u"a container."
        ),
        required=True,
        default=[u'index_html',
                 u'index.html',
                 u'index.htm',
                 u'FrontPage'],
        value_type=schema.TextLine()
    )

    roles_allowed_to_add_keywords = schema.List(
        title=_(u'Roles that can add keywords'),
        description=_(
            u"help_allow_roles_to_add_keywords",
            default=u"Only the following roles can add new keywords "),
        required=False,
        default=[
            u"Manager",
            u"Site Administrator",
            u"Reviewer",
        ],
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"),
    )


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
        title=_(u'label_first_weekday', default=u'First weekday'),
        description=_(
            u'help_first_weekday',
            default=u'First day in the week.'),
        required=True,
        default=None,
        vocabulary="plone.app.vocabularies.Weekdays")


class ITypesSchema(Interface):
    """Controlpanel settings for the types settings.
    """

    types_use_view_action_in_listings = schema.List(
        title=_(u'Types which use the view action in listing views.'),
        description=_(
            u"help_types_use_view_action_in_listings",
            default=u"When clicking items in listing views, these "
                    u"types will use the '/view' action instead of using "
                    u"their default view."),
        required=False,
        default=[u'Image',
                 u'File'],
        value_type=schema.TextLine(),
    )

    redirect_links = schema.Bool(
        title=_(u"Redirect links"),
        description=_(
            u"help_redirect_links",
            default=u"When clicking on a Link type, should the user be "
                    u"taken to the default view or be redirected to the "
                    u"Link's URL?"),
        required=False,
        default=True
    )

    default_page_types = schema.List(
        title=_(u"Types that can be set as a default page"),
        description=_(
            u"The content types that should be available for selection "
            u"when setting a default page."),
        required=False,
        default=[
            u'Document',
            u'Event',
            u'News Item',
        ],
        value_type=schema.TextLine()
    )


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

    email_from_address = schema.ASCIILine(
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

    email_charset = schema.ASCIILine(
        title=_(u"Email characterset"),
        description=_(u'Characterset to use when sending emails.'),
        default='utf-8',
        required=True,
    )


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


class ISocialMediaSchema(Interface):

    share_social_data = schema.Bool(
        title=_(u'Share social data'),
        description=_(u'Include meta tags on pages to give hints to '
                      u'social media on how to render your pages better '
                      u'when shared'),
        default=True)

    twitter_username = schema.TextLine(
        title=_(u'Twitter Username'),
        description=_(u'To idenitify things like Twitter Cards'),
        required=False,
        default=u'')

    facebook_app_id = schema.TextLine(
        title=_(u'Facebook app id'),
        description=_(u'To be used with some integrations like open graph data'),
        required=False,
        default=u'')

    facebook_username = schema.TextLine(
        title=_(u'Facebook username'),
        description=_(u'For linking open graph data to a facebook account'),
        required=False,
        default=u'')


class IImagingSchema(Interface):
    allowed_sizes = schema.List(
        title=_(u'Allowed image sizes'),
        description=_(u'Specify all allowed maximum image dimensions, '
                      'one per line. '
                      'The required format is &lt;name&gt; &lt;width&gt;:&lt;height&gt;.'),
        value_type=schema.TextLine(),
        default=[
            "large 768:768",
            "preview 400:400",
            "mini 200:200",
            "thumb 128:128",
            "tile 64:64",
            "icon 32:32",
            "listing 16:16"],
        required=False,
    )

    quality = schema.Int(
        title=_(u'Scaled image quality'),
        description=_(u'A value for the quality of scaled images, from 1 '
                      '(lowest) to 95 (highest). A value of 0 will mean '
                      'plone.scaling\'s default will be used, which is '
                      'currently 88.'),
        min=0,
        max=95,
        default=88
    )


class ILoginSchema(Interface):

    auth_cookie_length = schema.Int(
        title=_(u'Auth cookie length'),
        default=0,
        required=False
    )

    verify_login_name = schema.Bool(
        title=_(u'Verify login name'),
        default=True,
        required=False
    )

    allow_external_login_sites = schema.Tuple(
        title=_(u'Allow external login sites'),
        default=(),
        value_type=schema.ASCIILine(),
        required=False
    )

    external_login_url = schema.ASCIILine(
        title=_(u'External login url'),
        default=None,
        required=False
    )

    external_logout_url = schema.ASCIILine(
        title=_(u'External logout url'),
        default=None,
        required=False
    )

    external_login_iframe = schema.Bool(
        title=_(u'External login iframe'),
        default=False,
        required=False
    )


class ILinkSchema(Interface):

    external_links_open_new_window = schema.Bool(
        title=_(u'Open external links in new a window'),
        description=_(u''),
        default=False,
        required=False)

    mark_special_links = schema.Bool(
        title=_(u'Mark special links'),
        description=_(u'Marks external or special protocol links with class.'),
        default=True,
        required=False)
