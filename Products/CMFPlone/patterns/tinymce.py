from lxml import html
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.app.theming.utils import theming_policy
from plone.base.interfaces import IFilterSchema
from plone.base.interfaces import ITinyMCESchema
from plone.base.utils import safe_text
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import get_portal
from zope.component import getUtility

import json


class TinyMCESettingsGenerator:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.settings = getUtility(IRegistry).forInterface(
            ITinyMCESchema, prefix="plone", check=False
        )
        self.filter_settings = getUtility(IRegistry).forInterface(
            IFilterSchema, prefix="plone", check=False
        )
        self.nav_root = getNavigationRootObject(
            self.context,
            get_portal(),
        )
        self.nav_root_url = self.nav_root.absolute_url()

    def get_theme(self):
        return theming_policy().get_theme()

    def get_content_css(self, style_css=""):
        files = []
        if style_css:
            files.extend(style_css.split(","))
        content_css = self.settings.content_css or []
        for url in content_css:
            if url and url.strip():
                files.append("/".join([self.nav_root_url, url.strip()]))
        theme = self.get_theme()
        tinymce_content_css = getattr(theme, "tinymce_content_css", None)
        if tinymce_content_css is not None and tinymce_content_css != "":
            for path in theme.tinymce_content_css.split(","):
                if path.startswith("http://") or path.startswith("https://"):
                    files.append(path)
                else:
                    files.append(self.nav_root_url + path)

        return ",".join(files)

    def get_style_format(self, txt, _type="format", base=None):
        parts = txt.strip().split("|")
        if len(parts) < 2:
            return
        if base is None:
            val = {}
        else:
            val = base.copy()
        val.update({"title": parts[0], _type: parts[1]})
        if len(parts) > 2:
            val["icon"] = parts[2]
        return val

    def get_styles(self, styles, _type="format", base=None):
        result = []
        for style in styles:
            style = self.get_style_format(style, _type, base)
            if not style:
                continue
            result.append(style)
        return result

    def get_all_style_formats(self):
        header_styles = self.settings.header_styles or []
        block_styles = self.settings.block_styles or []
        inline_styles = self.settings.inline_styles or []
        alignment_styles = self.settings.alignment_styles or []
        table_styles = self.settings.table_styles or []
        style_formats = [
            {"title": "Headers", "items": self.get_styles(header_styles)},
            {"title": "Block", "items": self.get_styles(block_styles)},
            {"title": "Inline", "items": self.get_styles(inline_styles)},
            {"title": "Alignment", "items": self.get_styles(alignment_styles)},
            {
                "title": "Tables",
                "items": self.get_styles(
                    table_styles, "classes", {"selector": "table"}
                ),
            },
        ]
        return [sf for sf in style_formats if sf["items"]]

    def get_tiny_config(self):
        settings = self.settings
        importcss_file_filter = "tinymce-formats.css"

        theme = self.get_theme()
        extra_content_css = ""
        if theme and getattr(theme, "tinymce_styles_css", None):
            extra = ",{}/{}".format(
                self.nav_root_url, theme.tinymce_styles_css.lstrip("/")
            )
            extra_content_css += extra
            importcss_file_filter += extra

        tiny_config = {
            "resize": "both" if settings.resizing else False,
            "content_css": self.get_content_css() + extra_content_css,
            "plugins": ["plonelink", "ploneimage", "importcss"] + settings.plugins,
            "external_plugins": {},
            "toolbar": settings.toolbar,
            "entity_encoding": settings.entity_encoding,
            "importcss_append": True,
            "importcss_file_filter": importcss_file_filter,
            "browser_spellcheck": True,
            "table_default_styles": {},
            "table_default_attributes": {"class": "listing"},
            "table_advtab": False,
            "table_row_advtab": False,
            "table_cell_advtab": False,
            "table_style_by_css": False,
            "table_appearance_options": False,
        }
        toolbar_additions = settings.custom_buttons or []

        if settings.editor_height:
            tiny_config["height"] = settings.editor_height
        if settings.autoresize:
            tiny_config["plugins"].append("autoresize")
            tiny_config["autoresize_max_height"] = 1000  # hard coded?
        if settings.editor_width:
            tiny_config["width"] = settings.editor_width

        # specific plugin options
        if "contextmenu" in settings.plugins:
            tiny_config["contextmenu"] = (
                "plonelink ploneimage inserttable |" " cell row column deletetable"
            )

        if settings.libraries_spellchecker_choice == "AtD":
            mtool = getToolByName(self.context, "portal_membership")
            member = mtool.getAuthenticatedMember()
            member_id = member.getId()
            if member_id:
                if "compat3x" not in tiny_config["plugins"]:
                    tiny_config["plugins"].append("compat3x")
                tiny_config["external_plugins"][
                    "AtD"
                ] = "{}/++plone++static/tinymce-AtD-plugin/" "editor_plugin.js".format(
                    self.nav_root_url
                )
                # None when Anonymous User
                tiny_config["atd_rpc_id"] = "plone-" + member_id
                tiny_config["atd_rpc_url"] = self.nav_root_url
                tiny_config["atd_show_types"] = ",".join(
                    settings.libraries_atd_show_types
                )
                tiny_config["atd_ignore_strings"] = ",".join(
                    settings.libraries_atd_ignore_strings
                )
                toolbar_additions.append("AtD")
        elif settings.libraries_spellchecker_choice == "AtD":
            tiny_config["browser_spellcheck"] = True

        if toolbar_additions:
            tiny_config["toolbar"] += " | {}".format(" ".join(toolbar_additions))

        for plugin in settings.custom_plugins or []:
            parts = plugin.split("|")
            if len(parts) != 2:
                continue
            url = parts[1].strip()
            if not url:
                continue
            if url.find("//", 0, 8) == -1:
                # assuming relative/absolute w/out url scheme
                url = f"{self.nav_root_url}/{url}"
            tiny_config["external_plugins"][parts[0]] = url

        tiny_config["style_formats"] = self.get_all_style_formats()
        if settings.formats:
            try:
                tiny_config["formats"] = json.loads(settings.formats)
            except ValueError:
                pass

        if settings.menubar:
            tiny_config["menubar"] = settings.menubar
        if settings.menu:
            try:
                tiny_config["menu"] = json.loads(settings.menu)
            except ValueError:
                pass

        if hasattr(settings, "templates") and settings.templates:
            try:
                tiny_config["templates"] = json.loads(settings.templates)
            except ValueError:
                pass

        # add safe_html settings, which are used in backend for filtering:
        if not self.filter_settings.disable_filtering:
            valid_tags = self.filter_settings.valid_tags
            nasty_tags = self.filter_settings.nasty_tags
            custom_attributes = self.filter_settings.custom_attributes
            safe_attributes = [safe_text(attr) for attr in html.defs.safe_attrs]
            valid_attributes = safe_attributes + custom_attributes
            # valid_elements : 'a[href|target=_blank],strong/b,div[align],br'
            tiny_valid_elements = []
            for tag in valid_tags:
                tag_str = "{}[{}]".format(tag, "|".join(valid_attributes))
                tiny_valid_elements.append(tag_str)
            # We want to remove the nasty tag including the content in the
            # backend, so TinyMCE should allow them here.
            for tag in nasty_tags:
                tag_str = "{}[{}]".format(tag, "|".join(valid_attributes))
                tiny_valid_elements.append(tag_str)
            tiny_config["valid_elements"] = ",".join(tiny_valid_elements)

        if settings.other_settings:
            try:
                tiny_config.update(json.loads(settings.other_settings))
            except ValueError:
                pass

        return tiny_config
